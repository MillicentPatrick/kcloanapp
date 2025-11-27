import pandas as pd
import numpy as np

class FinancialProjections:
    def __init__(self, historical_data, assumptions):
        self.historical_data = historical_data
        self.assumptions = assumptions
    
    def project_income_statement(self, periods=5, loan_amount=0, interest_rate=0, repayment_period=0):
        """Project income statement with loan impact"""
        projections = []
        current_revenue = self.historical_data.get('revenue', 0)
        current_cogs = self.historical_data.get('cogs', 0)
        current_opex = self.historical_data.get('operating_expenses', 0)
        current_interest_expense = self.historical_data.get('interest_expense', 0)
        
        # Calculate additional interest expense from new loan
        if loan_amount > 0 and interest_rate > 0:
            monthly_interest = loan_amount * (interest_rate / 100) / 12
            additional_annual_interest = monthly_interest * 12
        else:
            additional_annual_interest = 0
        
        for year in range(1, periods + 1):
            revenue = current_revenue * (1 + self.assumptions.get('revenue_growth', 0.05)) ** year
            cogs = revenue * self.assumptions.get('cogs_percentage', 0.6)
            gross_profit = revenue - cogs
            opex = revenue * self.assumptions.get('opex_percentage', 0.25)
            ebitda = gross_profit - opex
            
            # Include interest expense in projections
            interest_expense = current_interest_expense + additional_annual_interest
            ebit = ebitda - interest_expense
            tax = ebit * self.assumptions.get('tax_rate', 0.3)
            net_income = ebit - tax
            
            projections.append({
                'year': year,
                'revenue': revenue,
                'cogs': cogs,
                'gross_profit': gross_profit,
                'operating_expenses': opex,
                'ebitda': ebitda,
                'interest_expense': interest_expense,
                'ebit': ebit,
                'tax': tax,
                'net_income': net_income,
                'loan_impact': additional_annual_interest
            })
        
        return pd.DataFrame(projections)
    
    def project_balance_sheet(self, income_projections, loan_amount=0):
        """Project balance sheet with loan impact"""
        projections = []
        current_assets = self.historical_data.get('total_assets', 0)
        current_liabilities = self.historical_data.get('total_liabilities', 0)
        current_equity = self.historical_data.get('equity', 0)
        current_debt = self.historical_data.get('long_term_debt', 0)
        
        for idx, year_data in income_projections.iterrows():
            year = year_data['year']
            net_income = year_data['net_income']
            
            # Include new loan in liabilities
            assets = current_assets * (1 + self.assumptions.get('asset_growth', 0.05)) ** year
            existing_liabilities = current_liabilities * (1 + self.assumptions.get('debt_growth', 0.03)) ** year
            
            # Add new loan to liabilities (amortizing over time)
            if loan_amount > 0:
                remaining_loan_balance = self._calculate_remaining_loan_balance(
                    loan_amount, year, self.assumptions.get('repayment_period', 60)
                )
                total_liabilities = existing_liabilities + remaining_loan_balance
            else:
                total_liabilities = existing_liabilities
                remaining_loan_balance = 0
            
            equity = current_equity + net_income * year  # Accumulated earnings
            
            projections.append({
                'year': year,
                'total_assets': assets,
                'total_liabilities': total_liabilities,
                'equity': equity,
                'current_assets': assets * 0.6,  # Simplified
                'current_liabilities': total_liabilities * 0.4,  # Simplified
                'loan_balance': remaining_loan_balance,
                'existing_debt': existing_liabilities
            })
        
        return pd.DataFrame(projections)
    
    def project_cash_flow(self, income_projections, balance_projections, loan_amount=0, repayment_schedule=None):
        """Project cash flow statement with loan impact"""
        projections = []
        
        for idx, (income_row, balance_row) in enumerate(zip(
            income_projections.iterrows(), balance_projections.iterrows())):
            
            year = income_row[1]['year']
            net_income = income_row[1]['net_income']
            interest_expense = income_row[1].get('interest_expense', 0)
            
            # Operating cash flow (starting with net income and adding back non-cash items)
            operating_cashflow = net_income + interest_expense  # Simplified: add back interest
            
            # Investing cash flow (capital expenditures)
            investing_cashflow = -balance_row[1]['total_assets'] * self.assumptions.get('capex_percentage', 0.1)
            
            # Financing cash flow (loan proceeds and repayments)
            if loan_amount > 0 and repayment_schedule is not None:
                # First year: receive loan, subsequent years: make payments
                if year == 1:
                    financing_cashflow = loan_amount  # Receive loan
                else:
                    # Calculate annual loan payment from repayment schedule
                    annual_payment = self._get_annual_loan_payment(repayment_schedule, year)
                    financing_cashflow = -annual_payment
            else:
                financing_cashflow = 0
            
            net_cashflow = operating_cashflow + investing_cashflow + financing_cashflow
            
            projections.append({
                'year': year,
                'operating_cashflow': operating_cashflow,
                'investing_cashflow': investing_cashflow,
                'financing_cashflow': financing_cashflow,
                'net_cashflow': net_cashflow,
                'loan_impact': financing_cashflow
            })
        
        return pd.DataFrame(projections)

    def calculate_loan_repayment_schedule(self, loan_amount, interest_rate, repayment_period):
        """Calculate loan repayment schedule"""
        monthly_rate = interest_rate / 12 / 100
        monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** repayment_period) / \
                         ((1 + monthly_rate) ** repayment_period - 1)
        
        schedule = []
        remaining_balance = loan_amount
        
        for month in range(1, repayment_period + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment
            
            schedule.append({
                'month': month,
                'payment': monthly_payment,
                'principal': principal_payment,
                'interest': interest_payment,
                'remaining_balance': max(0, remaining_balance)
            })
        
        return pd.DataFrame(schedule)
    
    def _calculate_remaining_loan_balance(self, loan_amount, year, repayment_period):
        """Calculate remaining loan balance for a given year"""
        if year > repayment_period / 12:  # Convert months to years
            return 0
        
        # Simplified calculation - in practice, use amortization formula
        annual_repayment = loan_amount / (repayment_period / 12)
        remaining_balance = max(0, loan_amount - (annual_repayment * (year - 1)))
        return remaining_balance
    
    def _get_annual_loan_payment(self, repayment_schedule, year):
        """Get annual loan payment from monthly repayment schedule"""
        if repayment_schedule is None or repayment_schedule.empty:
            return 0
        
        # Sum monthly payments for the given year
        start_month = (year - 1) * 12 + 1
        end_month = year * 12
        
        annual_payments = repayment_schedule[
            (repayment_schedule['month'] >= start_month) & 
            (repayment_schedule['month'] <= end_month)
        ]
        
        if not annual_payments.empty:
            return annual_payments['payment'].sum()
        return 0

    def calculate_debt_service_coverage_ratio(self, income_projections, repayment_schedule):
        """Calculate Debt Service Coverage Ratio (DSCR)"""
        dscr_data = []
        
        for idx, income_row in income_projections.iterrows():
            year = income_row['year']
            ebitda = income_row['ebitda']
            interest_expense = income_row.get('interest_expense', 0)
            
            # Get annual loan payment for this year
            annual_loan_payment = self._get_annual_loan_payment(repayment_schedule, year)
            
            # DSCR = EBITDA / Total Debt Service
            total_debt_service = interest_expense + annual_loan_payment
            
            if total_debt_service > 0:
                dscr = ebitda / total_debt_service
            else:
                dscr = float('inf')  # No debt service
                
            dscr_data.append({
                'year': year,
                'ebitda': ebitda,
                'total_debt_service': total_debt_service,
                'dscr': dscr,
                'status': 'Adequate' if dscr >= 1.25 else 'Inadequate'
            })
        
        return pd.DataFrame(dscr_data)