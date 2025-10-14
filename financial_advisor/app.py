import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import sys
import os

# Add the utils directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Now import from utils
try:
    from financial_calculators import FinancialCalculators
    from data_processor import DataProcessor
except ImportError:
    # If import fails, define the classes inline
    st.warning("Some modules couldn't be imported. Using inline definitions.")
    
    # Define FinancialCalculators inline if import fails
    class FinancialCalculators:
        @staticmethod
        def sip_calculator(monthly_investment, years, expected_return):
            monthly_rate = expected_return / 100 / 12
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

    # Define DataProcessor inline if import fails
    class DataProcessor:
        @staticmethod
        def process_user_financial_data(user_data):
            total_expenses = sum(user_data['expenses'].values())
            monthly_savings = user_data['monthly_income'] - total_expenses
            savings_rate = (monthly_savings / user_data['monthly_income']) * 100
            
            processed_data = user_data.copy()
            processed_data['derived_metrics'] = {
                'total_expenses': total_expenses,
                'monthly_savings': monthly_savings,
                'savings_rate': savings_rate,
                'desired_investment': user_data['monthly_income'] * (user_data['investment_percentage'] / 100)
            }
            
            expense_ratios = {}
            for category, amount in user_data['expenses'].items():
                expense_ratios[category] = (amount / user_data['monthly_income']) * 100
            
            processed_data['expense_ratios'] = expense_ratios
            return processed_data

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="WealthWise AI - Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem;
    border: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.alert-card {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.success-card {
    background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.sidebar .sidebar-content {
    background: #f0f2f6;
}
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data
        self.monthly_income = user_data['monthly_income']
        self.expenses = user_data['expenses']
        self.investment_pct = user_data['investment_percentage']
        
    def calculate_financial_metrics(self):
        total_expenses = sum(self.expenses.values())
        monthly_savings = self.monthly_income - total_expenses
        desired_investment = self.monthly_income * (self.investment_pct / 100)
        savings_rate = (monthly_savings / self.monthly_income) * 100
        
        expense_ratios = {category: (amount / self.monthly_income) * 100 
                         for category, amount in self.expenses.items()}
        
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
        
        if metrics['savings_rate'] < 10:
            alerts.append({
                'type': 'CRITICAL',
                'message': f"💸 Low savings rate: {metrics['savings_rate']:.1f}%",
                'suggestion': "Aim for at least 20% savings rate."
            })
        
        return alerts

def get_mutual_fund_data():
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
    st.sidebar.title("💰 WealthWise AI")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Navigation", 
                           ["🏠 Dashboard", "📊 Financial Analysis", "💰 Investment Insights", "🎯 Goal Planning"])
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip**: Regular tracking improves financial health by 40%")
    
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "📊 Financial Analysis":
        show_financial_analysis()
    elif menu == "💰 Investment Insights":
        show_investment_insights()
    elif menu == "🎯 Goal Planning":
        show_goal_planning()

def show_dashboard():
    st.markdown('<h1 class="main-header">💰 WealthWise AI Financial Dashboard</h1>', unsafe_allow_html=True)
    
    with st.form("financial_data"):
        st.subheader("📋 Enter Your Financial Details")
        
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
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = metrics['health_score'],
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
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💸 Expense Distribution")
            expenses_df = pd.DataFrame({
                'Category': [k.replace('_', ' ').title() for k in user_data['expenses'].keys()],
                'Amount': list(user_data['expenses'].values())
            })
            
            fig = px.pie(expenses_df, values='Amount', names='Category')
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Financial Ratios Analysis")
        
        ratios_data = {
            'Ratio': ['Savings Rate', 'Debt-to-Income', 'Investment Rate', 'Emergency Fund Coverage'],
            'Your Value': ['25%', '18%', '15%', '4.2 months'],
            'Recommended': ['>20%', '<30%', '>15%', '6 months'],
            'Status': ['✅ Good', '✅ Good', '✅ Good', '⚠️ Needs Improvement']
        }
        
        ratios_df = pd.DataFrame(ratios_data)
        st.dataframe(ratios_df, use_container_width=True)
    
    with col2:
        st.subheader("💡 Financial Recommendations")
        
        recommendations = [
            "🚀 Increase emergency fund to 6 months of expenses",
            "💰 Automate your investments for better consistency", 
            "📊 Review insurance coverage annually",
            "🎯 Set specific financial goals with timelines",
            "📱 Use budgeting apps to track daily expenses"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")

def show_investment_insights():
    st.markdown('<h1 class="main-header">💰 Investment Insights</h1>', unsafe_allow_html=True)
    
    mf_df = get_mutual_fund_data()
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📈 Mutual Fund Category Performance")
        
        category_avg = mf_df.groupby('Category').agg({
            '1_Year_Return': 'mean',
            '3_Year_CAGR': 'mean',
            '5_Year_CAGR': 'mean'
        }).round(2)
        
        fig = px.bar(category_avg, barmode='group', 
                    title="Average Returns by Fund Category")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚖️ Risk Categories")
        
        risk_counts = mf_df['Risk_Level'].value_counts()
        fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                    title="Distribution by Risk Level")
        st.plotly_chart(fig, use_container_width=True)
    
    # Investment Calculator
    st.subheader("💹 Investment Projection Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_investment = st.number_input("Monthly Investment (₹)", 1000, 100000, 5000, 500)
    with col2:
        investment_years = st.slider("Investment Period (Years)", 5, 30, 15)
    with col3:
        expected_return = st.slider("Expected Return (%)", 8, 20, 12)
    
    projection = FinancialCalculators.sip_calculator(monthly_investment, investment_years, expected_return)
    
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
                                ["Emergency Fund", "Down Payment", "Vacation", "Education", "Retirement"])
        
        goal_amount = st.number_input("Goal Amount (₹)", 10000, 10000000, 500000, 10000)
        timeline_years = st.slider("Timeline (Years)", 1, 30, 5)
        current_savings = st.number_input("Current Savings (₹)", 0, goal_amount, 0, 1000)
        
        if st.button("Calculate Monthly Savings"):
            months = timeline_years * 12
            monthly_saving = (goal_amount - current_savings) / months
            
            st.success(f"**Monthly Savings Needed:** ₹{monthly_saving:,.0f}")
            
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
        st.subheader("📋 Common Financial Goals Guide")
        
        goals_info = {
            'Emergency Fund': {
                'target': '6 months of expenses',
                'priority': 'High',
                'timeline': '6-12 months'
            },
            'Retirement': {
                'target': '25x annual expenses', 
                'priority': 'High',
                'timeline': '10+ years'
            },
            'Down Payment': {
                'target': '20% of property value',
                'priority': 'Medium', 
                'timeline': '2-5 years'
            }
        }
        
        for goal, info in goals_info.items():
            with st.expander(f"🎯 {goal}"):
                st.write(f"**Target:** {info['target']}")
                st.write(f"**Priority:** {info['priority']}")
                st.write(f"**Timeline:** {info['timeline']}")

if __name__ == "__main__":
    main()
