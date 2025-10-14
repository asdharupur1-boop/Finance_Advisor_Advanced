import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math

class FinancialCalculators:
    """
    Comprehensive financial calculators for various scenarios
    """
    
    @staticmethod
    def compound_interest(principal, annual_rate, years, monthly_contribution=0, compounding_frequency=12):
        """
        Calculate compound interest with regular contributions
        
        Args:
            principal (float): Initial investment amount
            annual_rate (float): Annual interest rate in percentage
            years (int): Investment period in years
            monthly_contribution (float): Monthly contribution amount
            compounding_frequency (int): Number of times interest compounds per year
        
        Returns:
            dict: Calculation results
        """
        rate_decimal = annual_rate / 100
        periods = years * compounding_frequency
        periodic_rate = rate_decimal / compounding_frequency
        
        # Future value of initial investment
        future_value_principal = principal * (1 + periodic_rate) ** periods
        
        # Future value of monthly contributions
        if monthly_contribution > 0:
            future_value_contributions = monthly_contribution * \
                (((1 + periodic_rate) ** periods - 1) / periodic_rate)
        else:
            future_value_contributions = 0
        
        total_future_value = future_value_principal + future_value_contributions
        total_contributions = principal + (monthly_contribution * periods)
        total_interest = total_future_value - total_contributions
        
        return {
            'future_value': total_future_value,
            'total_contributions': total_contributions,
            'total_interest': total_interest,
            'return_multiple': total_future_value / total_contributions if total_contributions > 0 else 0
        }
    
    @staticmethod
    def sip_calculator(monthly_investment, years, expected_return):
        """
        Calculate Systematic Investment Plan (SIP) returns
        
        Args:
            monthly_investment (float): Monthly investment amount
            years (int): Investment period in years
            expected_return (float): Expected annual return in percentage
        
        Returns:
            dict: SIP calculation results
        """
        monthly_rate = expected_return / 100 / 12
        months = years * 12
        
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        total_invested = monthly_investment * months
        estimated_returns = future_value - total_invested
        
        return {
            'future_value': future_value,
            'total_invested': total_invested,
            'estimated_returns': estimated_returns,
            'return_multiple': future_value / total_invested,
            'xirr': expected_return  # Since it's regular SIP, XIRR ≈ expected return
        }
    
    @staticmethod
    def emi_calculator(loan_amount, annual_interest_rate, loan_tenure_years):
        """
        Calculate Equated Monthly Installment (EMI) for loans
        
        Args:
            loan_amount (float): Principal loan amount
            annual_interest_rate (float): Annual interest rate in percentage
            loan_tenure_years (int): Loan tenure in years
        
        Returns:
            dict: EMI calculation results
        """
        monthly_interest_rate = annual_interest_rate / 100 / 12
        loan_tenure_months = loan_tenure_years * 12
        
        emi = loan_amount * monthly_interest_rate * \
              ((1 + monthly_interest_rate) ** loan_tenure_months) / \
              (((1 + monthly_interest_rate) ** loan_tenure_months) - 1)
        
        total_payment = emi * loan_tenure_months
        total_interest = total_payment - loan_amount
        
        return {
            'emi': emi,
            'total_payment': total_payment,
            'total_interest': total_interest,
            'interest_percentage': (total_interest / loan_amount) * 100
        }
    
    @staticmethod
    def inflation_adjustment(amount, years, inflation_rate=6):
        """
        Adjust amount for inflation to calculate future purchasing power
        
        Args:
            amount (float): Current amount
            years (int): Number of years in future
            inflation_rate (float): Expected inflation rate in percentage
        
        Returns:
            dict: Inflation adjustment results
        """
        future_value = amount * ((1 + inflation_rate/100) ** years)
        purchasing_power_loss = future_value - amount
        
        return {
            'current_value': amount,
            'future_value': future_value,
            'purchasing_power_loss': purchasing_power_loss,
            'inflation_impact': f"₹{amount:,.0f} today = ₹{future_value:,.0f} in {years} years"
        }
    
    @staticmethod
    def retirement_calculator(current_age, retirement_age, current_savings, monthly_contribution, 
                            expected_return, inflation_rate, retirement_expenses):
        """
        Comprehensive retirement planning calculator
        
        Args:
            current_age (int): Current age
            retirement_age (int): Planned retirement age
            current_savings (float): Current retirement savings
            monthly_contribution (float): Monthly retirement contribution
            expected_return (float): Expected annual return in percentage
            inflation_rate (float): Expected inflation rate in percentage
            retirement_expenses (float): Expected monthly expenses in retirement (today's value)
        
        Returns:
            dict: Retirement planning results
        """
        years_to_retirement = retirement_age - current_age
        retirement_years = 90 - retirement_age  # Assuming life expectancy of 90
        
        # Calculate corpus at retirement
        retirement_corpus = FinancialCalculators.compound_interest(
            current_savings, expected_return, years_to_retirement, monthly_contribution
        )['future_value']
        
        # Adjust retirement expenses for inflation
        inflated_retirement_expenses = retirement_expenses * ((1 + inflation_rate/100) ** years_to_retirement)
        annual_retirement_expenses = inflated_retirement_expenses * 12
        
        # Calculate required retirement corpus (25x annual expenses - 4% rule)
        required_corpus = annual_retirement_expenses * 25
        
        # Check if corpus is sufficient
        is_sufficient = retirement_corpus >= required_corpus
        shortfall = max(0, required_corpus - retirement_corpus)
        
        return {
            'retirement_corpus': retirement_corpus,
            'required_corpus': required_corpus,
            'is_sufficient': is_sufficient,
            'shortfall': shortfall,
            'annual_retirement_expenses': annual_retirement_expenses,
            'years_to_retirement': years_to_retirement,
            'retirement_years': retirement_years
        }
    
    @staticmethod
    def goal_planning_calculator(goal_amount, current_savings, timeline_years, expected_return=8):
        """
        Calculate monthly savings required for a financial goal
        
        Args:
            goal_amount (float): Target goal amount
            current_savings (float): Current savings for this goal
            timeline_years (int): Years to achieve the goal
            expected_return (float): Expected annual return in percentage
        
        Returns:
            dict: Goal planning results
        """
        # Future value of current savings
        future_value_current = FinancialCalculators.compound_interest(
            current_savings, expected_return, timeline_years
        )['future_value']
        
        # Additional amount needed
        additional_needed = max(0, goal_amount - future_value_current)
        
        # Monthly savings required
        if additional_needed > 0:
            monthly_savings = FinancialCalculators.pmt(
                expected_return/100/12, timeline_years*12, additional_needed
            )
        else:
            monthly_savings = 0
        
        return {
            'goal_amount': goal_amount,
            'future_value_current': future_value_current,
            'additional_needed': additional_needed,
            'monthly_savings_required': abs(monthly_savings),
            'is_achievable': additional_needed >= 0
        }
    
    @staticmethod
    def pmt(rate, nper, pv, fv=0, type=0):
        """
        Calculate the payment for a loan based on constant payments and a constant interest rate
        """
        if rate == 0:
            return -(fv + pv) / nper
        
        pvif = (1 + rate) ** nper
        pmt = (rate * (fv + pv * pvif)) / (pvif - 1)
        
        return -pmt
    
    @staticmethod
    def debt_snowball_calculator(debts, extra_payment=0, method='snowball'):
        """
        Calculate debt payoff strategy using snowball or avalanche method
        
        Args:
            debts (list): List of dictionaries with 'name', 'balance', 'interest_rate', 'min_payment'
            extra_payment (float): Additional monthly payment
            method (str): 'snowball' (smallest balance first) or 'avalanche' (highest interest first)
        
        Returns:
            dict: Debt payoff plan
        """
        debts_copy = [debt.copy() for debt in debts]
        
        if method == 'snowball':
            debts_copy.sort(key=lambda x: x['balance'])
        else:  # avalanche
            debts_copy.sort(key=lambda x: x['interest_rate'], reverse=True)
        
        total_interest_paid = 0
        months_to_payoff = 0
        payoff_plan = []
        
        while any(debt['balance'] > 0 for debt in debts_copy):
            months_to_payoff += 1
            monthly_extra = extra_payment
            
            for debt in debts_copy:
                if debt['balance'] <= 0:
                    continue
                
                # Calculate interest for the month
                monthly_interest = debt['balance'] * (debt['interest_rate'] / 100 / 12)
                total_interest_paid += monthly_interest
                
                # Total payment for this debt
                total_payment = debt['min_payment'] + monthly_extra
                monthly_extra = 0  # Use extra payment only for first debt in priority
                
                # Apply payment to debt
                principal_payment = min(total_payment - monthly_interest, debt['balance'])
                debt['balance'] -= principal_payment
                
                if debt['balance'] <= 0 and debt not in [p['debt'] for p in payoff_plan]:
                    payoff_plan.append({
                        'debt': debt['name'],
                        'payoff_month': months_to_payoff,
                        'total_interest': monthly_interest
                    })
        
        return {
            'total_months': months_to_payoff,
            'total_interest_paid': total_interest_paid,
            'payoff_plan': payoff_plan,
            'method_used': method
        }