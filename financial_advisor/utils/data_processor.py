import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class DataProcessor:
    """
    Data processing utilities for financial data analysis
    """
    
    @staticmethod
    def process_user_financial_data(user_data):
        """
        Process and validate user financial data
        
        Args:
            user_data (dict): Raw user financial data
        
        Returns:
            dict: Processed and validated data
        """
        processed_data = user_data.copy()
        
        # Calculate derived metrics
        total_expenses = sum(user_data['expenses'].values())
        monthly_savings = user_data['monthly_income'] - total_expenses
        savings_rate = (monthly_savings / user_data['monthly_income']) * 100
        
        processed_data['derived_metrics'] = {
            'total_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'savings_rate': savings_rate,
            'desired_investment': user_data['monthly_income'] * (user_data['investment_percentage'] / 100)
        }
        
        # Calculate expense ratios
        expense_ratios = {}
        for category, amount in user_data['expenses'].items():
            expense_ratios[category] = (amount / user_data['monthly_income']) * 100
        
        processed_data['expense_ratios'] = expense_ratios
        
        return processed_data
    
    @staticmethod
    def detect_spending_patterns(historical_data):
        """
        Analyze historical spending data to detect patterns
        
        Args:
            historical_data (list): List of monthly financial records
        
        Returns:
            dict: Detected patterns and insights
        """
        if not historical_data:
            return {}
        
        df = pd.DataFrame(historical_data)
        
        patterns = {
            'lifestyle_creep': DataProcessor._detect_lifestyle_creep(df),
            'seasonal_spending': DataProcessor._detect_seasonal_patterns(df),
            'category_trends': DataProcessor._analyze_category_trends(df),
            'savings_consistency': DataProcessor._analyze_savings_consistency(df)
        }
        
        return patterns
    
    @staticmethod
    def _detect_lifestyle_creep(df):
        """Detect if expenses are growing faster than income"""
        if len(df) < 3:
            return "Insufficient data for analysis"
        
        income_growth = (df['income'].iloc[-1] - df['income'].iloc[0]) / df['income'].iloc[0]
        expense_growth = (df['total_expenses'].iloc[-1] - df['total_expenses'].iloc[0]) / df['total_expenses'].iloc[0]
        
        if expense_growth > income_growth + 0.05:  # 5% threshold
            return f"Lifestyle creep detected: Expenses growing {expense_growth:.1%} vs income {income_growth:.1%}"
        else:
            return "No significant lifestyle creep detected"
    
    @staticmethod
    def _detect_seasonal_patterns(df):
        """Detect seasonal spending patterns"""
        if len(df) < 12:
            return "Need at least 12 months of data for seasonal analysis"
        
        # Simple seasonal detection - you can enhance this with proper time series analysis
        monthly_avg = df.groupby(df['date'].dt.month)['total_expenses'].mean()
        seasonal_variation = monthly_std = monthly_avg.std() / monthly_avg.mean()
        
        if seasonal_variation > 0.2:
            return f"Significant seasonal spending variation detected ({seasonal_variation:.1%})"
        else:
            return "Spending patterns are relatively consistent throughout the year"
    
    @staticmethod
    def _analyze_category_trends(df):
        """Analyze trends in spending categories"""
        category_trends = {}
        
        # Get numeric columns (expense categories)
        expense_columns = [col for col in df.columns if col not in ['date', 'income', 'total_expenses', 'savings']]
        
        for category in expense_columns:
            if len(df[category]) > 1:
                trend = np.polyfit(range(len(df)), df[category], 1)[0]  # Linear trend slope
                category_trends[category] = {
                    'trend': trend,
                    'direction': 'increasing' if trend > 0 else 'decreasing',
                    'magnitude': abs(trend)
                }
        
        return category_trends
    
    @staticmethod
    def _analyze_savings_consistency(df):
        """Analyze consistency of savings over time"""
        if len(df) < 3:
            return "Insufficient data for savings consistency analysis"
        
        savings_std = df['savings'].std()
        savings_cv = savings_std / df['savings'].mean()  # Coefficient of variation
        
        if savings_cv > 0.3:
            return f"High savings variability detected (CV: {savings_cv:.2f})"
        else:
            return f"Savings are relatively consistent (CV: {savings_cv:.2f})"
    
    @staticmethod
    def generate_financial_health_score(user_data, historical_data=None):
        """
        Generate a comprehensive financial health score (0-100)
        
        Args:
            user_data (dict): Current user financial data
            historical_data (list): Historical financial records
        
        Returns:
            dict: Health score and component scores
        """
        scores = {}
        
        # Savings Rate Score (0-25 points)
        savings_rate = user_data['derived_metrics']['savings_rate']
        savings_score = min(25, savings_rate)  # 1% savings = 1 point, max 25
        
        # Emergency Fund Score (0-20 points)
        # Assuming 3 months expenses as minimum emergency fund
        emergency_fund_months = 3  # This should come from user input
        emergency_score = min(20, (emergency_fund_months / 6) * 20)  # 6 months = perfect score
        
        # Debt Management Score (0-15 points)
        debt_ratio = (user_data['expenses'].get('loan_repayments', 0) + 
                     user_data['expenses'].get('rent_emi', 0)) / user_data['monthly_income']
        debt_score = max(0, 15 - (debt_ratio * 100))  # Lower debt ratio = higher score
        
        # Investment Rate Score (0-15 points)
        investment_score = min(15, user_data['investment_percentage'] * 0.75)  # 20% investment = 15 points
        
        # Expense Management Score (0-25 points)
        high_expense_categories = sum(1 for ratio in user_data['expense_ratios'].values() if ratio > 30)
        expense_score = max(0, 25 - (high_expense_categories * 5))
        
        total_score = savings_score + emergency_score + debt_score + investment_score + expense_score
        
        return {
            'total_score': total_score,
            'component_scores': {
                'savings_rate': savings_score,
                'emergency_fund': emergency_score,
                'debt_management': debt_score,
                'investment_rate': investment_score,
                'expense_management': expense_score
            },
            'interpretation': DataProcessor._interpret_health_score(total_score)
        }
    
    @staticmethod
    def _interpret_health_score(score):
        """Interpret the financial health score"""
        if score >= 80:
            return "Excellent - Strong financial health"
        elif score >= 60:
            return "Good - Solid financial foundation"
        elif score >= 40:
            return "Fair - Room for improvement"
        else:
            return "Needs Attention - Significant improvements needed"
    
    @staticmethod
    def create_sample_historical_data(user_data, months=12):
        """
        Create sample historical data for demonstration
        """
        historical_data = []
        base_date = datetime.now() - timedelta(days=30*months)
        
        for i in range(months):
            record_date = base_date + timedelta(days=30*i)
            
            # Add some random variation to simulate real data
            variation = np.random.normal(1, 0.1)  # 10% variation
            
            monthly_record = {
                'date': record_date,
                'income': user_data['monthly_income'] * variation,
                'total_expenses': sum(user_data['expenses'].values()) * variation,
                'savings': (user_data['monthly_income'] - sum(user_data['expenses'].values())) * variation
            }
            
            # Add individual expense categories with variation
            for category, amount in user_data['expenses'].items():
                category_variation = np.random.normal(1, 0.15)  # 15% variation for categories
                monthly_record[category] = amount * category_variation
            
            historical_data.append(monthly_record)
        
        return historical_data
    
    @staticmethod
    def export_financial_report(user_data, analysis_results, file_format='json'):
        """
        Export financial analysis report
        
        Args:
            user_data (dict): User financial data
            analysis_results (dict): Analysis results
            file_format (str): Export format ('json', 'csv')
        
        Returns:
            str: Exported data in requested format
        """
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'user_data': user_data,
            'analysis_results': analysis_results,
            'summary': {
                'financial_health_score': analysis_results.get('health_score', {}).get('total_score', 0),
                'key_insights': analysis_results.get('key_insights', []),
                'recommendations': analysis_results.get('recommendations', [])
            }
        }
        
        if file_format == 'json':
            return json.dumps(report_data, indent=2, default=str)
        elif file_format == 'csv':
            # Create a flattened version for CSV
            flat_data = []
            # Implementation for CSV export would go here
            return "CSV export functionality to be implemented"
        else:
            raise ValueError(f"Unsupported format: {file_format}")