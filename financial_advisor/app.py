import streamlit as st
import math

# Simple configuration
st.set_page_config(
    page_title="Simple Wealth Guide",
    page_icon="💰",
    layout="centered"
)

# No external CSS - using native Streamlit styling
st.title("💰 Simple Wealth Guide")
st.markdown("### Your Minimal Financial Companion")

# Financial calculations without external libraries
def calculate_future_value(monthly_investment, years, annual_return):
    """Calculate future value of monthly investments"""
    monthly_rate = annual_return / 100 / 12
    months = years * 12
    future_value = monthly_investment * ((1 + monthly_rate) ** months - 1) / monthly_rate
    return future_value

def analyze_finances(income, expenses_dict, investment_percent):
    """Analyze financial health"""
    total_expenses = sum(expenses_dict.values())
    savings = income - total_expenses
    savings_rate = (savings / income) * 100 if income > 0 else 0
    investment_amount = income * (investment_percent / 100)
    
    return {
        'total_expenses': total_expenses,
        'savings': savings,
        'savings_rate': savings_rate,
        'investment_amount': investment_amount
    }

# Main app
def main():
    # Input Section
    with st.form("financial_input"):
        st.subheader("📥 Your Financial Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_income = st.number_input("Monthly Income (₹)", 
                                           min_value=1000, value=50000, step=1000)
            investment_percent = st.slider("Investment Target (%)", 0, 50, 15)
        
        with col2:
            st.subheader("Monthly Expenses")
            rent = st.number_input("Rent/EMI", value=15000, step=500)
            food = st.number_input("Food & Groceries", value=8000, step=500)
            transport = st.number_input("Transport", value=4000, step=200)
            other = st.number_input("Other Expenses", value=7000, step=500)
        
        submitted = st.form_submit_button("Analyze My Finances")
    
    if submitted:
        expenses = {
            'Rent/EMI': rent,
            'Food': food,
            'Transport': transport,
            'Other': other
        }
        
        results = analyze_finances(monthly_income, expenses, investment_percent)
        
        # Display Results
        st.success("✅ Analysis Complete!")
        
        st.subheader("📊 Financial Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Income", f"₹{monthly_income:,}")
        with col2:
            st.metric("Expenses", f"₹{results['total_expenses']:,}")
        with col3:
            st.metric("Savings", f"₹{results['savings']:,}")
        with col4:
            st.metric("Savings Rate", f"{results['savings_rate']:.1f}%")
        
        # Financial Health
        st.subheader("❤️ Financial Health")
        
        if results['savings_rate'] >= 20:
            st.success("**Excellent!** You're saving more than 20% of your income.")
        elif results['savings_rate'] >= 10:
            st.warning("**Good!** Try to reach 20% savings rate.")
        else:
            st.error("**Needs improvement.** Focus on increasing your savings rate.")
        
        # Investment Section
        st.subheader("💡 Investment Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Monthly Investment Target:** ₹{results['investment_amount']:,.0f}")
            
            if results['savings'] >= results['investment_amount']:
                st.success("🎯 You can meet your investment target!")
            else:
                shortfall = results['investment_amount'] - results['savings']
                st.warning(f"⚠️ Shortfall: ₹{shortfall:,.0f}")
                st.write("Consider reducing expenses or increasing income")
        
        with col2:
            st.write("**Quick Tips:**")
            tips = [
                "• Save at least 20% of income",
                "• Build 6-month emergency fund",
                "• Start investing early",
                "• Avoid unnecessary debt"
            ]
            for tip in tips:
                st.write(tip)
        
        # Future Projections
        st.subheader("📈 Future Projections")
        
        if results['investment_amount'] > 0:
            investment_amount = results['investment_amount']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # 5 years
                future_5y = calculate_future_value(investment_amount, 5, 12)
                st.metric("5 Years", f"₹{future_5y:,.0f}")
            
            with col2:
                # 10 years
                future_10y = calculate_future_value(investment_amount, 10, 12)
                st.metric("10 Years", f"₹{future_10y:,.0f}")
            
            with col3:
                # 15 years
                future_15y = calculate_future_value(investment_amount, 15, 12)
                st.metric("15 Years", f"₹{future_15y:,.0f}")
        
        # Expense Breakdown
        st.subheader("💸 Expense Breakdown")
        
        for category, amount in expenses.items():
            percentage = (amount / monthly_income) * 100
            st.write(f"**{category}:** ₹{amount:,} ({percentage:.1f}%)")
            
            # Simple progress bar using text
            bars = "█" * int(percentage / 5)  # Each █ represents 5%
            st.progress(int(percentage))
        
        # Recommendations
        st.subheader("🎯 Recommendations")
        
        if expenses['Rent/EMI'] / monthly_income > 0.3:
            st.write("• **Consider:** Your rent is high. Look for more affordable options")
        
        if results['savings_rate'] < 15:
            st.write("• **Action needed:** Focus on increasing your savings rate")
        
        if results['investment_amount'] == 0:
            st.write("• **Start investing:** Even small amounts can grow significantly")
        
        st.write("• **Emergency fund:** Build 3-6 months of expenses as safety net")
        st.write("• **Review regularly:** Check your finances monthly")

if __name__ == "__main__":
    main()
