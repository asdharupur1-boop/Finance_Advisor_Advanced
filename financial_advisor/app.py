import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =================================================================================
# 1. CORE FINANCIAL LOGIC (ADAPTED FROM NOTEBOOK)
# =================================================================================

class FinancialAnalyzer:
    """Class to perform core financial calculations based on user input."""
    def __init__(self, monthly_income, expenses, investment_pct):
        self.monthly_income = monthly_income
        self.expenses = expenses
        self.investment_pct = investment_pct / 100
        self.metrics = self.calculate_financial_metrics()

    def calculate_financial_metrics(self):
        """Calculate key financial metrics."""
        # Clean up expense keys for display
        cleaned_expenses = {k.replace('_', ' ').title(): v for k, v in self.expenses.items()}
        total_expenses = sum(cleaned_expenses.values())
        
        monthly_savings = self.monthly_income - total_expenses
        desired_investment = self.monthly_income * self.investment_pct
        
        # Handle zero income gracefully
        savings_rate = (monthly_savings / self.monthly_income * 100) if self.monthly_income else 0
        
        expense_ratios = {category: (amount / self.monthly_income * 100)
                         for category, amount in cleaned_expenses.items()}
        
        # Calculate a simple Health Score (based on savings rate)
        health_score = min(100, max(0, int(savings_rate * 3 + 40)))
        
        return {
            'total_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'desired_investment': desired_investment,
            'savings_rate': savings_rate,
            'expense_ratios': expense_ratios,
            'health_score': health_score
        }
    
    def generate_spending_alerts(self):
        """Generate alerts for high spending categories."""
        alerts = []
        high_spending_threshold = 25  # % of income
        
        # Check if desired investment is feasible
        if self.metrics['desired_investment'] > self.metrics['monthly_savings']:
            shortage = self.metrics['desired_investment'] - self.metrics['monthly_savings']
            alerts.append({
                'severity': '⚠️ Investment Gap',
                'message': f"To meet your {self.investment_pct*100:.0f}% target, you need ₹{shortage:,.0f} more savings monthly. Consider reducing expenses or increasing income.",
                'icon': '🚨'
            })
        
        # Check high expense categories
        for category, ratio in self.metrics['expense_ratios'].items():
            if ratio >= high_spending_threshold:
                alerts.append({
                    'severity': f'📉 High {category} Spend',
                    'message': f"{category} consumes {ratio:.1f}% of your income. Review this area for potential savings.",
                    'icon': '🔥'
                })
        
        if self.metrics['savings_rate'] < 10:
             alerts.append({
                'severity': '🛑 Low Savings Rate',
                'message': f"Your savings rate is low at {self.metrics['savings_rate']:.1f}%. Aim for 15-20% for strong financial security.",
                'icon': '⬇️'
            })
            
        if not alerts:
            alerts.append({'severity': '✅ Great Job!', 'message': 'No critical spending issues detected. Your budget looks healthy!', 'icon': '👍'})
            
        return alerts

    def investment_projection_calculator(self, monthly_investment, years, expected_return):
        """Project future value of SIP using compounding."""
        monthly_rate = expected_return / 100 / 12
        months = years * 12
        
        if monthly_rate == 0:
            future_value = monthly_investment * months # Simple calculation if rate is 0
        else:
            future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        
        total_invested = monthly_investment * months
        estimated_returns = future_value - total_invested
        return future_value, total_invested, estimated_returns
    
    def generate_projection_df(self, monthly_investment):
        """Generates a DataFrame for investment projections."""
        projections = []
        for years in [5, 10, 15, 20]:
            for rate in [8, 12, 15]:
                future_value, total_invested, estimated_returns = self.investment_projection_calculator(
                    monthly_investment, years, rate
                )
                projections.append({
                    'Period (Years)': years,
                    'Return Rate (%)': f'{rate}%',
                    'Total Invested (₹)': total_invested,
                    'Estimated Value (₹)': future_value,
                    'Potential Gains (₹)': estimated_returns
                })
        return pd.DataFrame(projections)

# =================================================================================
# 2. STREAMLIT UI COMPONENTS
# =================================================================================

def display_metric_card(title, value, delta=None, color='text-gray-900', icon='💰'):
    """Custom function to display a professional metric card with Tailwind-like styling."""
    
    # Simple color mapping for icons/text based on value
    if 'Savings Rate' in title:
        if value > 20:
            icon_color = 'bg-green-100 text-green-700'
        elif value > 10:
            icon_color = 'bg-yellow-100 text-yellow-700'
        else:
            icon_color = 'bg-red-100 text-red-700'
    elif 'Health Score' in title:
         if value > 75:
            icon_color = 'bg-green-100 text-green-700'
         elif value > 50:
            icon_color = 'bg-yellow-100 text-yellow-700'
         else:
            icon_color = 'bg-red-110 text-red-700'
    else:
        icon_color = 'bg-blue-100 text-blue-700'
        
    
    html_string = f"""
    <div style="background-color: #f9f9f9; padding: 16px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%; border-left: 5px solid {icon_color.split()[1].replace('text-', '')};">
        <div style="font-size: 14px; color: #6b7280; font-weight: 500;">{title}</div>
        <div style="font-size: 24px; font-weight: 700; color: {color}; margin-top: 4px;">
            {icon} {value}
        </div>
    </div>
    """
    st.markdown(html_string, unsafe_allow_html=True)

def create_charts(analyzer):
    """Generate Plotly charts for the dashboard."""
    metrics = analyzer.metrics
    
    # 1. Expense Breakdown Pie Chart
    expense_df = pd.DataFrame(list(metrics['expense_ratios'].items()), columns=['Category', 'Ratio'])
    expense_df['Amount'] = expense_df['Ratio'] * analyzer.monthly_income / 100
    
    fig_pie = px.pie(
        expense_df,
        values='Amount',
        names='Category',
        title='Monthly Expense Breakdown (₹)',
        hole=.4,
        color_discrete_sequence=px.colors.sequential.Agsunset,
    )
    fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    fig_pie.update_layout(height=400, margin={"t":50, "b":0, "l":0, "r":0}, showlegend=True,
                          font=dict(family="Inter", size=12))
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # 2. Financial Health Bar Chart
    financial_df = pd.DataFrame({
        'Category': ['Income', 'Expenses', 'Savings'],
        'Amount': [analyzer.monthly_income, metrics['total_expenses'], metrics['monthly_savings']]
    })
    
    fig_bar = px.bar(
        financial_df,
        x='Category',
        y='Amount',
        title='Income vs Expenses vs Savings (₹)',
        color='Category',
        color_discrete_map={
            'Income': 'rgb(75, 192, 192)', 
            'Expenses': 'rgb(255, 99, 132)', 
            'Savings': 'rgb(54, 162, 235)'
        }
    )
    fig_bar.update_layout(height=400, xaxis_title="", yaxis_title="Amount (₹)", 
                          font=dict(family="Inter", size=12))
    st.plotly_chart(fig_bar, use_container_width=True)

def create_mf_chart(mf_df):
    """Create chart for mutual fund returns analysis."""
    # Calculate average returns by category
    category_performance = mf_df.groupby('Category')[['1_Year_Return', '3_Year_CAGR', '5_Year_CAGR']].mean().reset_index()

    fig = go.Figure()

    for period in ['1_Year_Return', '3_Year_CAGR', '5_Year_CAGR']:
        fig.add_trace(go.Bar(
            x=category_performance['Category'],
            y=category_performance[period],
            name=period.replace('_', ' ').replace('CAGR', 'Return'),
            marker_line_width=0,
            opacity=0.75
        ))

    fig.update_layout(
        barmode='group',
        title='Average Mutual Fund Returns by Category',
        xaxis_title="Fund Category",
        yaxis_title="Average Returns (%)",
        legend_title="Return Period",
        height=450,
        font=dict(family="Inter", size=12),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

# =================================================================================
# 3. STREAMLIT PAGE SETUP
# =================================================================================

# --- Data Input Setup (Simulating notebook input) ---
# Hardcode default values based on the notebook run (cell 2 output)
DEFAULT_DATA = {
    'income': 45000,
    'rent_emi': 5000,
    'utilities': 1000,
    'internet_phone': 500,
    'loan_repayments': 12000,
    'insurance': 200,
    'subscriptions': 799,
    'groceries': 4500,
    'dining_entertainment': 6000,
    'transportation': 3000,
    'shopping': 5000,
    'miscellaneous': 1500,
    'investment_pct': 15.0
}

@st.cache_data
def get_mutual_fund_returns_data():
    """Returns sample mutual fund data."""
    mf_data = {
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
    return pd.DataFrame(mf_data)

mf_df = get_mutual_fund_returns_data()


# --- Streamlit Main App ---

st.set_page_config(
    page_title="AI Financial Health Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    # Light, professional theme
)

# Custom CSS for the light/professional look
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Overall Light Theme container */
    .stApp {
        background-color: #f7f9fd; /* Very light blue/grey for background */
    }
    
    /* Header styling */
    h1 {
        font-weight: 800;
        color: #1f2937; /* Dark gray */
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc { /* Targeting Streamlit sidebar elements */
        background-color: #ffffff !important;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Metric Card Styling (using the custom display_metric_card function for visual appeal) */
    .st-emotion-cache-1r6r062 { /* Target for st.markdown output */
        padding-top: 0 !important;
    }
    
    /* Styling for the Alerts Box */
    .alert-box {
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #fff;
        border: 1px solid #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🤖 AI Financial Health Dashboard")
st.markdown("---")

# =================================================================================
# 4. SIDEBAR INPUTS
# =================================================================================

with st.sidebar:
    st.header("Financial Data Input (₹)")
    
    # Income Input
    income = st.number_input(
        "Monthly Take-Home Income:", 
        min_value=0, 
        value=DEFAULT_DATA['income'], 
        step=1000
    )
    
    st.subheader("Monthly Expenses:")
    
    # Fixed Expenses
    col_fixed1, col_fixed2 = st.columns(2)
    with col_fixed1:
        rent_emi = st.number_input("Rent/EMI:", min_value=0, value=DEFAULT_DATA['rent_emi'], step=100)
        loan_repayments = st.number_input("Loan Repayments:", min_value=0, value=DEFAULT_DATA['loan_repayments'], step=100)
        groceries = st.number_input("Groceries:", min_value=0, value=DEFAULT_DATA['groceries'], step=100)
        transportation = st.number_input("Transportation:", min_value=0, value=DEFAULT_DATA['transportation'], step=50)

    with col_fixed2:
        utilities = st.number_input("Utilities:", min_value=0, value=DEFAULT_DATA['utilities'], step=50)
        insurance = st.number_input("Insurance:", min_value=0, value=DEFAULT_DATA['insurance'], step=50)
        dining_entertainment = st.number_input("Dining & Entertainment:", min_value=0, value=DEFAULT_DATA['dining_entertainment'], step=100)
        shopping = st.number_input("Shopping:", min_value=0, value=DEFAULT_DATA['shopping'], step=100)
    
    # Other smaller expenses
    internet_phone = st.number_input("Internet/Phone:", min_value=0, value=DEFAULT_DATA['internet_phone'], step=50)
    subscriptions = st.number_input("Subscriptions:", min_value=0, value=DEFAULT_DATA['subscriptions'], step=10)
    miscellaneous = st.number_input("Miscellaneous:", min_value=0, value=DEFAULT_DATA['miscellaneous'], step=50)

    # Investment Goal
    investment_pct = st.slider(
        "Target Investment Percentage of Income (%)",
        min_value=0, max_value=50, value=DEFAULT_DATA['investment_pct'], step=1
    )

# --- Aggregate Expenses ---
expenses_dict = {
    'rent_emi': rent_emi,
    'utilities': utilities,
    'internet_phone': internet_phone,
    'loan_repayments': loan_repayments,
    'insurance': insurance,
    'subscriptions': subscriptions,
    'groceries': groceries,
    'dining_entertainment': dining_entertainment,
    'transportation': transportation,
    'shopping': shopping,
    'miscellaneous': miscellaneous
}

# Instantiate the analyzer
analyzer = FinancialAnalyzer(income, expenses_dict, investment_pct)
metrics = analyzer.metrics

# =================================================================================
# 5. DASHBOARD LAYOUT
# =================================================================================

# --- Row 1: Key Metrics ---
st.header("1. Financial Snapshot")
col1, col2, col3, col4 = st.columns(4)

with col1:
    display_metric_card("Monthly Income", f"₹{income:,.0f}", icon='💵')
with col2:
    display_metric_card("Total Expenses", f"₹{metrics['total_expenses']:,.0f}", icon='💸')
with col3:
    display_metric_card("Net Monthly Savings", f"₹{metrics['monthly_savings']:,.0f}", icon='🏦')
with col4:
    display_metric_card("Savings Rate", f"{metrics['savings_rate']:.1f}%", icon='📈')

# --- Row 2: Health Score and Alerts ---
st.markdown("<br>", unsafe_allow_html=True)
col_alerts, col_score = st.columns([3, 1])

with col_alerts:
    st.subheader("Actionable Alerts & Insights")
    st.markdown('<div class="alert-box">', unsafe_allow_html=True)
    alerts = analyzer.generate_spending_alerts()
    for alert in alerts:
        st.markdown(f"**{alert['icon']} {alert['severity']}:** {alert['message']}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_score:
    st.subheader("Financial Health Score")
    # Custom display for Health Score to look like a gauge/big number
    display_metric_card(
        "AI Assessment Score", 
        f"{metrics['health_score']}/100", 
        color='#4f46e5', 
        icon='❤️'
    )


# --- Row 3: Visual Breakdown ---
st.markdown("---")
st.header("2. Detailed Financial Breakdown")

col_vis1, col_vis2 = st.columns(2)
with col_vis1:
    create_charts(analyzer) # Contains Pie and Bar charts

# --- Row 4: Investment Projection & Mutual Funds ---
st.markdown("---")
st.header("3. Investment Analysis")

if metrics['desired_investment'] > 0:
    # Projection Sub-section
    st.subheader(f"Future Value Projection (SIP: ₹{metrics['desired_investment']:,.0f} / Month)")
    
    projection_df = analyzer.generate_projection_df(metrics['desired_investment'])
    
    # Create an interactive line chart for projections
    fig_proj = px.line(
        projection_df,
        x='Period (Years)',
        y='Estimated Value (₹)',
        color='Return Rate (%)',
        title='Wealth Growth over Time',
        markers=True
    )
    fig_proj.update_layout(height=450, font=dict(family="Inter", size=12))
    st.plotly_chart(fig_proj, use_container_width=True)
    
    # Mutual Fund Sub-section
    st.subheader("Mutual Fund Performance Averages")
    create_mf_chart(mf_df)

    st.caption("Disclaimer: Mutual fund data is sample data for informational purposes only and does not constitute financial advice.")

else:
    st.warning("⚠️ Your current monthly savings (₹0) are less than your total expenses. Adjust your income or expenses to begin investment analysis.")


# --- Row 5: Raw Data Table ---
st.markdown("---")
st.header("4. Raw Data Tables")

st.subheader("Expense Ratios (% of Income)")
ratio_df = pd.DataFrame(list(metrics['expense_ratios'].items()), columns=['Category', 'Ratio (%)'])
st.dataframe(ratio_df.sort_values(by='Ratio (%)', ascending=False), use_container_width=True)

st.subheader("Full Sample Mutual Fund Data")
st.dataframe(mf_df, use_container_width=True)

# --- Conclusion ---
st.markdown(
    """
    <br>
    <div style="text-align: center; color: #6b7280; font-size: 14px;">
        Powered by AI Financial Analyzer | Dashboard built with Streamlit & Plotly
    </div>
    """,
    unsafe_allow_html=True
)
