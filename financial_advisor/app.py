import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Try to import Plotly with error handling
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("📊 Plotly not available. Using Streamlit native charts instead.")

# Page configuration
st.set_page_config(
    page_title="WealthMaster AI - Complete Financial Suite",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #4ECDC4;
    }
    .metric-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .fund-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

class MutualFundAnalyzer:
    def __init__(self):
        self.fund_data = self.generate_mutual_fund_data()
    
    def generate_mutual_fund_data(self):
        """Comprehensive mutual fund database with historical returns"""
        categories = {
            'Large Cap': 12,
            'Mid Cap': 15, 
            'Small Cap': 18,
            'Flexi Cap': 14,
            'ELSS': 16,
            'Sectoral': 20,
            'Hybrid': 11,
            'Debt': 8,
            'Index': 13
        }
        
        funds = []
        for category, base_return in categories.items():
            for i in range(3):
                fund_name = f"{category} Fund {i+1}"
                
                returns_6m = base_return * 0.5 + np.random.normal(0, 2)
                returns_1y = base_return + np.random.normal(0, 3)
                returns_3y = base_return + np.random.normal(0, 2)
                returns_5y = base_return + np.random.normal(0, 1.5)
                
                risk_level = self.get_risk_level(category)
                
                funds.append({
                    'Fund Name': fund_name,
                    'Category': category,
                    '6M Return': max(5, returns_6m),
                    '1Y Return': max(8, returns_1y),
                    '3Y CAGR': max(10, returns_3y),
                    '5Y CAGR': max(12, returns_5y),
                    'Risk Level': risk_level,
                    'Expense Ratio': round(0.5 + np.random.random() * 1.5, 2),
                    'Minimum SIP': 500,
                    'Fund Size (Cr)': np.random.randint(100, 5000)
                })
        
        return pd.DataFrame(funds)
    
    def get_risk_level(self, category):
        risk_map = {
            'Large Cap': 'Moderate',
            'Mid Cap': 'High', 
            'Small Cap': 'Very High',
            'Flexi Cap': 'Moderately High',
            'ELSS': 'High',
            'Sectoral': 'Very High',
            'Hybrid': 'Moderate',
            'Debt': 'Low',
            'Index': 'Moderate'
        }
        return risk_map.get(category, 'Moderate')
    
    def recommend_funds(self, savings_rate, investment_horizon, risk_appetite):
        df = self.fund_data.copy()
        
        risk_filters = {
            'Conservative': ['Low', 'Moderate'],
            'Moderate': ['Low', 'Moderate', 'Moderately High'],
            'Aggressive': ['Low', 'Moderate', 'Moderately High', 'High', 'Very High']
        }
        
        filtered_funds = df[df['Risk Level'].isin(risk_filters.get(risk_appetite, ['Moderate']))]
        
        return_columns = {
            '6 months': '6M Return',
            '1 year': '1Y Return', 
            '3 years': '3Y CAGR',
            '5 years': '5Y CAGR'
        }
        
        return_col = return_columns.get(investment_horizon, '3Y CAGR')
        
        filtered_funds['Score'] = (
            filtered_funds[return_col] * 0.6 +
            (100 - filtered_funds['Expense Ratio'] * 10) * 0.2 +
            (filtered_funds['5Y CAGR'] if return_col != '5Y CAGR' else 0) * 0.2
        )
        
        recommendations = filtered_funds.nlargest(5, 'Score')
        return recommendations
    
    def get_category_performance(self):
        return self.fund_data.groupby('Category').agg({
            '6M Return': 'mean',
            '1Y Return': 'mean',
            '3Y CAGR': 'mean', 
            '5Y CAGR': 'mean',
            'Risk Level': 'first'
        }).round(2).reset_index()

def create_simple_gauge(value, title, max_value=100):
    """Create a simple gauge using Streamlit components"""
    progress = value / max_value
    color = "🟢" if progress > 0.7 else "🟡" if progress > 0.4 else "🔴"
    
    st.write(f"**{title}**: {value:.1f} / {max_value} {color}")
    st.progress(progress)

def display_mutual_funds_with_fallback(metrics):
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.header("📈 Mutual Fund Analysis & Recommendations")
    
    mf_data = metrics['mutual_funds']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Recommended Risk Appetite", mf_data['risk_appetite'])
    with col2:
        st.metric("Based on Savings Rate", f"{metrics['basic']['savings_rate']:.1f}%")
    
    # Category Performance
    st.subheader("🏆 Category-wise Performance")
    category_df = pd.DataFrame(mf_data['category_performance'])
    
    if PLOTLY_AVAILABLE:
        fig = px.bar(category_df, x='Category', y=['6M Return', '1Y Return', '3Y CAGR', '5Y CAGR'],
                    title="Average Returns by Fund Category", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback: Show data table
        st.dataframe(category_df, use_container_width=True)
    
    # Time-based Recommendations
    st.subheader("🎯 Personalized Fund Recommendations")
    
    horizons = ['6 months', '1 year', '3 years', '5 years']
    selected_horizon = st.selectbox("Select Investment Horizon", horizons)
    
    if selected_horizon in mf_data['recommendations']:
        recommendations = mf_data['recommendations'][selected_horizon]
        
        if recommendations:
            st.write(f"**Top 5 Funds for {selected_horizon} horizon:**")
            
            for i, fund in enumerate(recommendations, 1):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**{i}. {fund['Fund Name']}**")
                        st.write(f"*Category: {fund['Category']}*")
                        st.write(f"Risk: {fund['Risk Level']}")
                    
                    with col2:
                        returns_map = {
                            '6 months': fund['6M Return'],
                            '1 year': fund['1Y Return'],
                            '3 years': fund['3Y CAGR'],
                            '5 years': fund['5Y CAGR']
                        }
                        return_val = returns_map[selected_horizon]
                        st.metric("Return", f"{return_val:.1f}%")
                    
                    with col3:
                        st.metric("5Y CAGR", f"{fund['5Y CAGR']:.1f}%")
                    
                    with col4:
                        st.metric("Expense Ratio", f"{fund['Expense Ratio']}%")
                    
                    st.markdown("---")
    
    # Fund Explorer
    st.subheader("🔍 Mutual Fund Explorer")
    all_funds_df = pd.DataFrame(mf_data['all_funds'])
    
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("Filter by Category", ['All'] + list(all_funds_df['Category'].unique()))
    with col2:
        selected_risk = st.selectbox("Filter by Risk", ['All'] + list(all_funds_df['Risk Level'].unique()))
    
    filtered_funds = all_funds_df.copy()
    if selected_category != 'All':
        filtered_funds = filtered_funds[filtered_funds['Category'] == selected_category]
    if selected_risk != 'All':
        filtered_funds = filtered_funds[filtered_funds['Risk Level'] == selected_risk]
    
    if not filtered_funds.empty:
        st.dataframe(
            filtered_funds[['Fund Name', 'Category', '1Y Return', '3Y CAGR', '5Y CAGR', 'Risk Level', 'Expense Ratio']],
            use_container_width=True,
            height=300
        )
    else:
        st.info("No funds match the selected criteria.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">🏆 WealthMaster AI</div>', unsafe_allow_html=True)
    st.markdown("### Complete Financial Analysis Suite with Mutual Fund Intelligence")
    
    # Show Plotly status
    if not PLOTLY_AVAILABLE:
        st.info("🔧 Using simplified visualizations. For enhanced charts, ensure Plotly is installed.")
    
    # User Input Section
    with st.sidebar:
        st.header("📊 Financial Profile")
        
        monthly_income = st.number_input("Monthly Income (₹)", 10000, 500000, 75000, 5000)
        current_age = st.slider("Current Age", 20, 65, 30)
        investment_percentage = st.slider("Investment Target (%)", 0, 50, 20)
        current_savings = st.number_input("Current Savings (₹)", 0, 10000000, 50000, 5000)
        retirement_savings = st.number_input("Retirement Corpus (₹)", 0, 50000000, 100000, 10000)
        
        st.header("💸 Monthly Expenses")
        expenses = {}
        expenses['rent_emi'] = st.number_input("Rent/EMI", 0, 100000, 20000, 1000)
        expenses['groceries'] = st.number_input("Groceries", 0, 50000, 12000, 500)
        expenses['transportation'] = st.number_input("Transportation", 0, 30000, 6000, 500)
        expenses['utilities'] = st.number_input("Utilities", 0, 20000, 4000, 200)
        expenses['entertainment'] = st.number_input("Entertainment", 0, 30000, 8000, 500)
        expenses['loan_repayments'] = st.number_input("Loan Repayments", 0, 50000, 10000, 1000)
        expenses['other'] = st.number_input("Other Expenses", 0, 40000, 5000, 500)
    
    user_data = {
        'monthly_income': monthly_income,
        'expenses': expenses,
        'investment_percentage': investment_percentage,
        'current_age': current_age,
        'current_savings': current_savings,
        'retirement_savings': retirement_savings
    }
    
    if st.button("🚀 Run Complete Financial Analysis", use_container_width=True):
        # Initialize analyzer
        analyzer = MutualFundAnalyzer()
        
        # Calculate basic metrics
        income = user_data['monthly_income']
        total_expenses = sum(user_data['expenses'].values())
        savings = income - total_expenses
        savings_rate = (savings / income) * 100
        
        # Get mutual fund recommendations
        if savings_rate >= 30:
            risk_appetite = 'Aggressive'
        elif savings_rate >= 15:
            risk_appetite = 'Moderate'
        else:
            risk_appetite = 'Conservative'
        
        horizons = ['6 months', '1 year', '3 years', '5 years']
        recommendations = {}
        
        for horizon in horizons:
            recs = analyzer.recommend_funds(savings_rate, horizon, risk_appetite)
            recommendations[horizon] = recs.to_dict('records')
        
        category_performance = analyzer.get_category_performance()
        
        metrics = {
            'basic': {
                'income': income,
                'expenses': total_expenses,
                'savings': savings,
                'savings_rate': savings_rate,
                'investment_amount': income * (user_data['investment_percentage'] / 100)
            },
            'mutual_funds': {
                'risk_appetite': risk_appetite,
                'recommendations': recommendations,
                'category_performance': category_performance.to_dict('records'),
                'all_funds': analyzer.fund_data.to_dict('records')
            }
        }
        
        # Display results in tabs
        tab1, tab2 = st.tabs(["📈 Financial Overview", "📊 Mutual Funds"])
        
        with tab1:
            display_financial_overview(metrics, user_data)
        
        with tab2:
            display_mutual_funds_with_fallback(metrics)

def display_financial_overview(metrics, user_data):
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.header("📈 Financial Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Income", f"₹{metrics['basic']['income']:,.0f}")
    with col2:
        st.metric("Total Expenses", f"₹{metrics['basic']['expenses']:,.0f}")
    with col3:
        st.metric("Monthly Savings", f"₹{metrics['basic']['savings']:,.0f}")
    with col4:
        st.metric("Savings Rate", f"{metrics['basic']['savings_rate']:.1f}%")
    
    # Financial Health Score
    health_score = min(100, metrics['basic']['savings_rate'] * 2 + 40)
    
    if PLOTLY_AVAILABLE:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Financial Health Score"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#4ECDC4"},
                   'steps': [{'range': [0, 40], 'color': "lightcoral"},
                            {'range': [40, 70], 'color': "lightyellow"},
                            {'range': [70, 100], 'color': "lightgreen"}]}
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        create_simple_gauge(health_score, "Financial Health Score")
    
    # Expense Breakdown
    st.subheader("💸 Expense Breakdown")
    expenses = user_data['expenses']
    
    for category, amount in expenses.items():
        percentage = (amount / metrics['basic']['income']) * 100
        st.write(f"**{category.replace('_', ' ').title()}**: ₹{amount:,} ({percentage:.1f}%)")
        st.progress(percentage / 100)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
