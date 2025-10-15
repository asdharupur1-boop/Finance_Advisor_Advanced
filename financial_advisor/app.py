import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Simple configuration
st.set_page_config(
    page_title="WealthGuide AI",
    page_icon="💰",
    layout="wide"
)

# Minimal CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 1.5rem;
        color: #374151;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

class SimpleFinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data
    
    def calculate_metrics(self):
        income = self.user_data['monthly_income']
        expenses = sum(self.user_data['expenses'].values())
        savings = income - expenses
        savings_rate = (savings / income) * 100
        
        return {
            'income': income,
            'expenses': expenses,
            'savings': savings,
            'savings_rate': savings_rate,
            'investment_amount': income * (self.user_data['investment_percentage'] / 100)
        }

def main():
    # Clean Header
    st.markdown('<div class="main-header">💰 WealthGuide AI</div>', unsafe_allow_html=True)
    st.markdown("### Your Simple Financial Companion")
    
    # Input Section
    with st.form("financial_input"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Income & Investment")
            monthly_income = st.number_input("Monthly Income (₹)", min_value=10000, value=50000, step=1000)
            investment_percentage = st.slider("Investment Target (%)", 0, 50, 20)
        
        with col2:
            st.subheader("Monthly Expenses")
            rent = st.number_input("Rent/EMI", value=15000, step=500)
            groceries = st.number_input("Groceries", value=8000, step=500)
            transportation = st.number_input("Transportation", value=4000, step=200)
            utilities = st.number_input("Utilities", value=3000, step=200)
            entertainment = st.number_input("Entertainment", value=5000, step=500)
            other = st.number_input("Other Expenses", value=3000, step=200)
        
        submitted = st.form_submit_button("Analyze My Finances")
    
    if submitted:
        user_data = {
            'monthly_income': monthly_income,
            'expenses': {
                'rent': rent,
                'groceries': groceries,
                'transportation': transportation,
                'utilities': utilities,
                'entertainment': entertainment,
                'other': other
            },
            'investment_percentage': investment_percentage
        }
        
        analyzer = SimpleFinancialAnalyzer(user_data)
        metrics = analyzer.calculate_metrics()
        
        # Display Key Metrics
        st.success("✅ Analysis Complete!")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Monthly Income", f"₹{metrics['income']:,.0f}")
        with col2:
            st.metric("Total Expenses", f"₹{metrics['expenses']:,.0f}")
        with col3:
            st.metric("Monthly Savings", f"₹{metrics['savings']:,.0f}")
        with col4:
            st.metric("Savings Rate", f"{metrics['savings_rate']:.1f}%")
        
        # Visualizations
        st.markdown('<div class="section-header">📊 Financial Overview</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Expense Breakdown
            expense_data = {
                'Category': list(user_data['expenses'].keys()),
                'Amount': list(user_data['expenses'].values())
            }
            df_expenses = pd.DataFrame(expense_data)
            
            fig = px.pie(df_expenses, values='Amount', names='Category', 
                        title="Expense Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Income vs Expenses
            categories = ['Income', 'Expenses', 'Savings']
            amounts = [metrics['income'], metrics['expenses'], metrics['savings']]
            
            fig = px.bar(x=categories, y=amounts, 
                        color=categories,
                        color_discrete_map={'Income': '#10b981', 'Expenses': '#ef4444', 'Savings': '#3b82f6'},
                        title="Income vs Expenses vs Savings")
            fig.update_layout(xaxis_title="", yaxis_title="Amount (₹)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Investment Section
        st.markdown('<div class="section-header">💡 Investment Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Investment")
            st.info(f"**Target Investment:** ₹{metrics['investment_amount']:,.0f}")
            
            if metrics['savings'] >= metrics['investment_amount']:
                st.success("🎯 You can meet your investment target!")
            else:
                st.warning(f"⚠️ You need ₹{metrics['investment_amount'] - metrics['savings']:,.0f} more to meet your target")
        
        with col2:
            st.subheader("Quick Tips")
            tips = [
                "💡 Aim for 20% savings rate",
                "📊 Track expenses weekly", 
                "🎯 Automate your investments",
                "🚀 Start emergency fund first"
            ]
            for tip in tips:
                st.write(tip)
        
        # Simple Projections
        st.markdown('<div class="section-header">📈 Future Projections</div>', unsafe_allow_html=True)
        
        if metrics['investment_amount'] > 0:
            # Simple SIP calculation
            monthly_investment = metrics['investment_amount']
            years = 10
            expected_return = 12
            
            monthly_rate = expected_return / 100 / 12
            months = years * 12
            future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Monthly Investment", f"₹{monthly_investment:,.0f}")
            with col2:
                st.metric("Investment Period", f"{years} years")
            with col3:
                st.metric("Potential Value", f"₹{future_value:,.0f}")

if __name__ == "__main__":
    main()
