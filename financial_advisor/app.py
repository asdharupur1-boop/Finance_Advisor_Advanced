import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
# Add these imports at the top of app.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from financial_calculators import FinancialCalculators
from data_processor import DataProcessor

# Then update the FinancialAnalyzer class to use these utilities:

class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data
        self.monthly_income = user_data['monthly_income']
        self.expenses = user_data['expenses']
        self.investment_pct = user_data['investment_percentage']
        self.financial_goals = user_data.get('financial_goals', {})
        
        # Process data using DataProcessor
        self.processed_data = DataProcessor.process_user_financial_data(user_data)
        
    def calculate_financial_metrics(self):
        return self.processed_data['derived_metrics']
    
    def generate_spending_alerts(self):
        metrics = self.calculate_financial_metrics()
        alerts = []
        
        # Use DataProcessor for advanced analysis
        health_score = DataProcessor.generate_financial_health_score(self.processed_data)
        
        # Spending category alerts
        for category, ratio in self.processed_data['expense_ratios'].items():
            if ratio > 35:
                alerts.append({
                    'type': 'CRITICAL',
                    'message': f"🚨 {category.replace('_', ' ').title()} is {ratio:.1f}% of income!",
                    'suggestion': "Consider significant reduction in this category."
                })
            elif ratio > 25:
                alerts.append({
                    'type': 'WARNING', 
                    'message': f"⚠️ {category.replace('_', ' ').title()} is {ratio:.1f}% of income",
                    'suggestion': "Monitor this expense category closely."
                })
        
        # Add health score alert
        if health_score['total_score'] < 40:
            alerts.append({
                'type': 'CRITICAL',
                'message': f"🏥 Financial Health Score: {health_score['total_score']}/100",
                'suggestion': "Immediate attention needed to improve financial health."
            })
        
        return alerts
    
    def investment_projection(self, monthly_investment, years=20, return_rate=12):
        # Use FinancialCalculators for more accurate projections
        return FinancialCalculators.sip_calculator(monthly_investment, years, return_rate)

# Page configuration
st.set_page_config(
    page_title="WealthWise AI - Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem;
    }
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data
        self.monthly_income = user_data['monthly_income']
        self.expenses = user_data['expenses']
        self.investment_pct = user_data['investment_percentage']
        self.financial_goals = user_data.get('financial_goals', {})
        
    def calculate_financial_metrics(self):
        total_expenses = sum(self.expenses.values())
        monthly_savings = self.monthly_income - total_expenses
        desired_investment = self.monthly_income * (self.investment_pct / 100)
        savings_rate = (monthly_savings / self.monthly_income) * 100
        
        expense_ratios = {category: (amount / self.monthly_income) * 100 
                         for category, amount in self.expenses.items()}
        
        # Financial health score (0-100)
        health_score = min(100, max(0, savings_rate * 2 + 30))
        
        return {
            'total_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'desired_investment': desired_investment,
            'savings_rate': savings_rate,
            'expense_ratios': expense_ratios,
            'health_score': health_score
        }
    
    def generate_spending_alerts(self):
        metrics = self.calculate_financial_metrics()
        alerts = []
        
        # Spending category alerts
        for category, ratio in metrics['expense_ratios'].items():
            if ratio > 35:
                alerts.append({
                    'type': 'CRITICAL',
                    'message': f"🚨 {category.replace('_', ' ').title()} is {ratio:.1f}% of income!",
                    'suggestion': "Consider significant reduction in this category."
                })
            elif ratio > 25:
                alerts.append({
                    'type': 'WARNING', 
                    'message': f"⚠️ {category.replace('_', ' ').title()} is {ratio:.1f}% of income",
                    'suggestion': "Monitor this expense category closely."
                })
        
        # Savings alerts
        if metrics['savings_rate'] < 10:
            alerts.append({
                'type': 'CRITICAL',
                'message': f"💸 Low savings rate: {metrics['savings_rate']:.1f}%",
                'suggestion': "Aim for at least 20% savings rate."
            })
        
        return alerts
    
    def investment_projection(self, monthly_investment, years=20, return_rate=12):
        monthly_rate = return_rate / 100 / 12
        months = years * 12
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        total_invested = monthly_investment * months
        returns = future_value - total_invested
        
        return {
            'future_value': future_value,
            'total_invested': total_invested,
            'returns': returns,
            'return_multiple': future_value / total_invested
        }

def get_mutual_fund_data():
    """Sample mutual fund data"""
    data = {
        'Category': ['Large Cap', 'Large Cap', 'Flexi Cap', 'Flexi Cap', 'ELSS', 'ELSS', 
                    'Mid Cap', 'Mid Cap', 'Small Cap', 'Small Cap', 'Hybrid', 'Hybrid',
                    'Debt', 'Debt', 'Index', 'Index'],
        'Fund_Name': ['ABC Bluechip Fund', 'XYZ Large Cap Fund', 'PQR Flexi Cap Fund', 
                     'LMN Dynamic Fund', 'Tax Saver Pro', 'Future Growth ELSS',
                     'Mid Cap Opportunities', 'Emerging Stars Fund', 'Small Cap Champion',
                     'Micro Marvel Fund', 'Balanced Advantage', 'Hybrid Wealth',
                     'Corporate Bond Fund', 'Gilt Fund', 'Nifty 50 Index', 'Sensex Index'],
        '1_Year_Return': [12.5, 11.8, 15.2, 14.7, 16.3, 15.8, 18.9, 20.1, 22.5, 24.3, 11.2, 10.8, 7.8, 8.2, 12.1, 11.9],
        '3_Year_CAGR': [14.2, 13.8, 16.5, 15.9, 17.2, 16.8, 19.5, 20.8, 23.1, 25.2, 12.1, 11.7, 8.5, 8.9, 13.8, 13.5],
        '5_Year_CAGR': [13.8, 13.2, 15.8, 15.2, 16.5, 16.1, 18.2, 19.1, 21.5, 23.8, 11.5, 11.2, 8.2, 8.5, 13.2, 12.9],
        'Risk_Level': ['Medium', 'Medium', 'Medium-High', 'Medium-High', 'High', 'High',
                      'High', 'High', 'Very High', 'Very High', 'Low-Medium', 'Low-Medium',
                      'Low', 'Low', 'Medium', 'Medium']
    }
    return pd.DataFrame(data)

def main():
    # Sidebar
    st.sidebar.image("https://img.icons8.com/fluency/96/money-bag.png", width=80)
    st.sidebar.title("WealthWise AI")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Navigation", 
                           ["🏠 Dashboard", "📊 Financial Analysis", "💰 Investment Insights", "🎯 Goal Planning", "📈 Progress Tracker"])
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip**: Regular tracking improves financial health by 40%")
    
    # Main content based on menu selection
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "📊 Financial Analysis":
        show_financial_analysis()
    elif menu == "💰 Investment Insights":
        show_investment_insights()
    elif menu == "🎯 Goal Planning":
        show_goal_planning()
    elif menu == "📈 Progress Tracker":
        show_progress_tracker()

def show_dashboard():
    st.markdown('<h1 class="main-header">💰 WealthWise AI Financial Dashboard</h1>', unsafe_allow_html=True)
    
    # User input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Enter Your Financial Details")
        
        with st.form("financial_data"):
            monthly_income = st.number_input("Monthly Take-home Income (₹)", min_value=10000, value=50000, step=1000)
            
            st.subheader("💸 Monthly Expenses")
            col1, col2 = st.columns(2)
            
            with col1:
                rent_emi = st.number_input("Rent/EMI (₹)", value=15000, step=500)
                utilities = st.number_input("Utilities (₹)", value=3000, step=100)
                internet_phone = st.number_input("Internet/Phone (₹)", value=1000, step=100)
                loan_repayments = st.number_input("Loan Repayments (₹)", value=5000, step=500)
                insurance = st.number_input("Insurance (₹)", value=2000, step=100)
            
            with col2:
                groceries = st.number_input("Groceries (₹)", value=7000, step=500)
                dining_entertainment = st.number_input("Dining & Entertainment (₹)", value=4000, step=500)
                transportation = st.number_input("Transportation (₹)", value=3000, step=100)
                shopping = st.number_input("Shopping (₹)", value=3000, step=500)
                miscellaneous = st.number_input("Miscellaneous (₹)", value=2500, step=100)
            
            investment_percentage = st.slider("Investment Target (% of Income)", 0, 50, 15)
            
            submitted = st.form_submit_button("Analyze My Finances")
    
    if submitted:
        user_data = {
            'monthly_income': monthly_income,
            'expenses': {
                'rent_emi': rent_emi,
                'utilities': utilities,
                'internet_phone': internet_phone,
                'loan_repayments': loan_repayments,
                'insurance': insurance,
                'groceries': groceries,
                'dining_entertainment': dining_entertainment,
                'transportation': transportation,
                'shopping': shopping,
                'miscellaneous': miscellaneous
            },
            'investment_percentage': investment_percentage
        }
        
        analyzer = FinancialAnalyzer(user_data)
        metrics = analyzer.calculate_financial_metrics()
        alerts = analyzer.generate_spending_alerts()
        
        # Display metrics
        st.success("✅ Financial Analysis Complete!")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Monthly Income", f"₹{metrics['monthly_income']:,.0f}")
        with col2:
            st.metric("Total Expenses", f"₹{metrics['total_expenses']:,.0f}")
        with col3:
            st.metric("Monthly Savings", f"₹{metrics['monthly_savings']:,.0f}")
        with col4:
            st.metric("Savings Rate", f"{metrics['savings_rate']:.1f}%")
        
        # Financial Health Score
        st.subheader("🏥 Financial Health Score")
        health_score = metrics['health_score']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = health_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Financial Health Score"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightcoral"},
                    {'range': [40, 70], 'color': "lightyellow"},
                    {'range': [70, 100], 'color': "lightgreen"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Alerts
        if alerts:
            st.subheader("🚨 Spending Alerts")
            for alert in alerts:
                if alert['type'] == 'CRITICAL':
                    st.error(f"{alert['message']} - {alert['suggestion']}")
                else:
                    st.warning(f"{alert['message']} - {alert['suggestion']}")
        else:
            st.success("🎉 No critical spending issues detected! Your budget looks healthy.")
        
        # Expense Breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💸 Expense Distribution")
            expenses_df = pd.DataFrame({
                'Category': [k.replace('_', ' ').title() for k in user_data['expenses'].keys()],
                'Amount': list(user_data['expenses'].values())
            })
            
            fig = px.pie(expenses_df, values='Amount', names='Category', 
                        color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Income vs Expenses")
            categories = ['Income', 'Expenses', 'Savings']
            amounts = [metrics['monthly_income'], metrics['total_expenses'], metrics['monthly_savings']]
            
            fig = px.bar(x=categories, y=amounts, 
                        color=categories,
                        color_discrete_map={'Income': 'green', 'Expenses': 'red', 'Savings': 'blue'})
            fig.update_layout(xaxis_title="", yaxis_title="Amount (₹)")
            st.plotly_chart(fig, use_container_width=True)

def show_financial_analysis():
    st.markdown('<h1 class="main-header">📊 Deep Financial Analysis</h1>', unsafe_allow_html=True)
    
    st.info("This section provides detailed analysis of your financial health and spending patterns.")
    
    # Sample analysis - in real app, this would use user data
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Spending Trends")
        
        # Simulated monthly data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        income = [50000, 51000, 52000, 53000, 54000, 55000]
        expenses = [42000, 43000, 44000, 45000, 46000, 47000]
        savings = [8000, 8000, 8000, 8000, 8000, 8000]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=income, mode='lines+markers', name='Income', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=months, y=expenses, mode='lines+markers', name='Expenses', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=months, y=savings, mode='lines+markers', name='Savings', line=dict(color='blue')))
        
        fig.update_layout(title="6-Month Financial Trend", xaxis_title="Month", yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Financial Ratios")
        
        ratios = {
            'Savings Rate': '25%',
            'Debt-to-Income': '18%',
            'Emergency Fund Coverage': '4.2 months',
            'Investment Rate': '15%'
        }
        
        for ratio, value in ratios.items():
            st.metric(ratio, value)
        
        st.subheader("💡 Recommendations")
        recommendations = [
            "Increase emergency fund to 6 months of expenses",
            "Consider debt consolidation for high-interest loans",
            "Automate your investments for better consistency",
            "Review insurance coverage annually"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")

def show_investment_insights():
    st.markdown('<h1 class="main-header">💰 Investment Insights</h1>', unsafe_allow_html=True)
    
    mf_df = get_mutual_fund_data()
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📈 Mutual Fund Performance")
        
        # Category-wise average returns
        category_avg = mf_df.groupby('Category').agg({
            '1_Year_Return': 'mean',
            '3_Year_CAGR': 'mean',
            '5_Year_CAGR': 'mean'
        }).round(2)
        
        fig = px.bar(category_avg, barmode='group', 
                    title="Average Returns by Fund Category")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚖️ Risk-Return Analysis")
        
        risk_return = mf_df.groupby('Risk_Level').agg({
            '3_Year_CAGR': ['mean', 'std']
        }).round(2)
        
        st.dataframe(risk_return)
        
        st.subheader("🔍 Top Performers")
        top_funds = mf_df.nlargest(5, '3_Year_CAGR')[['Fund_Name', 'Category', '3_Year_CAGR', 'Risk_Level']]
        st.dataframe(top_funds)
    
    # Investment Calculator
    st.subheader("💹 Investment Projection Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_investment = st.number_input("Monthly Investment (₹)", 1000, 100000, 5000, 500)
    with col2:
        investment_years = st.slider("Investment Period (Years)", 5, 30, 15)
    with col3:
        expected_return = st.slider("Expected Return (%)", 8, 20, 12)
    
    analyzer = FinancialAnalyzer({'monthly_income': 50000, 'expenses': {}, 'investment_percentage': 10})
    projection = analyzer.investment_projection(monthly_investment, investment_years, expected_return)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"₹{projection['total_invested']:,.0f}")
    with col2:
        st.metric("Future Value", f"₹{projection['future_value']:,.0f}")
    with col3:
        st.metric("Estimated Returns", f"₹{projection['returns']:,.0f}")

def show_goal_planning():
    st.markdown('<h1 class="main-header">🎯 Financial Goal Planning</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Set Your Financial Goals")
        
        goal_type = st.selectbox("Goal Type", 
                                ["Emergency Fund", "Down Payment", "Vacation", "Education", "Retirement", "Custom"])
        
        goal_amount = st.number_input("Goal Amount (₹)", 10000, 10000000, 500000, 10000)
        timeline_years = st.slider("Timeline (Years)", 1, 30, 5)
        current_savings = st.number_input("Current Savings (₹)", 0, goal_amount, 0, 1000)
        
        if st.button("Calculate Monthly Savings"):
            months = timeline_years * 12
            monthly_saving = (goal_amount - current_savings) / months
            
            st.success(f"**Monthly Savings Needed:** ₹{monthly_saving:,.0f}")
            
            # Progress visualization
            progress = min(100, (current_savings / goal_amount) * 100)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = progress,
                title = {'text': f"Goal Progress: {goal_type}"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightcoral"},
                        {'range': [50, 100], 'color': "lightgreen"}]
                }))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📋 Common Financial Goals")
        
        goals = {
            'Emergency Fund': {'amount': '6 months expenses', 'priority': 'High', 'timeline': '6-12 months'},
            'Retirement': {'amount': '25x annual expenses', 'priority': 'High', 'timeline': '10+ years'},
            'Down Payment': {'amount': '20% property value', 'priority': 'Medium', 'timeline': '2-5 years'},
            'Vacation': {'amount': '₹50,000-₹200,000', 'priority': 'Low', 'timeline': '6-18 months'}
        }
        
        for goal, details in goals.items():
            with st.expander(f"🎯 {goal}"):
                st.write(f"**Target:** {details['amount']}")
                st.write(f"**Priority:** {details['priority']}")
                st.write(f"**Timeline:** {details['timeline']}")

def show_progress_tracker():
    st.markdown('<h1 class="main-header">📈 Financial Progress Tracker</h1>', unsafe_allow_html=True)
    
    st.info("Track your financial journey and celebrate milestones!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Net Worth Tracker")
        
        # Sample net worth data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        assets = [500000, 520000, 545000, 570000, 600000, 630000]
        liabilities = [200000, 190000, 180000, 170000, 160000, 150000]
        net_worth = [a - l for a, l in zip(assets, liabilities)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=assets, mode='lines+markers', name='Assets', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=months, y=liabilities, mode='lines+markers', name='Liabilities', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=months, y=net_worth, mode='lines+markers', name='Net Worth', line=dict(color='blue')))
        
        fig.update_layout(title="Net Worth Growth Over Time", xaxis_title="Month", yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Financial Milestones")
        
        milestones = [
            {"milestone": "💰 First ₹1 Lakh Saved", "achieved": True, "date": "2023-03-15"},
            {"milestone": "🚗 Car Loan Paid Off", "achieved": True, "date": "2023-06-20"},
            {"milestone": "🏠 Emergency Fund Complete", "achieved": False, "date": "Target: 2024-12"},
            {"milestone": "📈 ₹10 Lakh Investment", "achieved": False, "date": "Target: 2025-06"}
        ]
        
        for milestone in milestones:
            if milestone['achieved']:
                st.success(f"✅ {milestone['milestone']} - {milestone['date']}")
            else:
                st.info(f"🎯 {milestone['milestone']} - {milestone['date']}")
        
        st.subheader("📅 Monthly Progress")
        current_month = datetime.now().strftime("%B")
        
        progress_data = {
            'Category': ['Savings Rate', 'Investment', 'Debt Reduction', 'Net Worth'],
            'Progress': [75, 60, 80, 65],
            'Target': [80, 75, 100, 80]
        }
        
        progress_df = pd.DataFrame(progress_data)
        
        fig = px.bar(progress_df, x='Category', y=['Progress', 'Target'], 
                    barmode='group', title=f"{current_month} Progress vs Target")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()