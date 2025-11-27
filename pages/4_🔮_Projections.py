import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from modules.projections import FinancialProjections
from utils.helpers import Helpers

def main():
    st.title("🔮 Financial Projections")
    
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in first")
        return
    
    # Check if assumptions are set
    if 'assumptions' not in st.session_state or not st.session_state.assumptions:
        st.error("Please set your assumptions on the Assumptions page first")
        return
    
    st.header("Loan Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        loan_amount = st.number_input(
            "Loan Amount (KES)",
            min_value=0,
            max_value=1000000000,
            value=st.session_state.get('loan_amount', 5000000),
            step=100000,
            key="projections_loan_amount"
        )
    
    with col2:
        interest_rate = st.number_input(
            "Interest Rate (%)",
            min_value=0.0,
            max_value=30.0,
            value=st.session_state.get('interest_rate', 12.5),
            step=0.1,
            key="projections_interest_rate"
        )
    
    with col3:
        repayment_period = st.number_input(
            "Repayment Period (Months)",
            min_value=1,
            max_value=120,
            value=st.session_state.get('repayment_period', 36),
            key="projections_repayment_period"
        )
    
    # Store loan parameters in session state
    st.session_state.loan_amount = loan_amount
    st.session_state.interest_rate = interest_rate
    st.session_state.repayment_period = repayment_period
    
    st.header("Projection Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        projection_years = st.slider(
            "Projection Period (Years)",
            min_value=1,
            max_value=10,
            value=5,
            key="projection_years"
        )
    
    with col2:
        base_revenue = st.number_input(
            "Base Revenue (KES)",
            min_value=0,
            max_value=1000000000,
            value=10000000,
            step=100000,
            key="base_revenue"
        )
    
    # Historical data (simulated - in real app, this would come from uploaded files)
    historical_data = {
        'revenue': base_revenue,
        'cogs': base_revenue * st.session_state.assumptions.get('cogs_percentage', 0.6),
        'operating_expenses': base_revenue * st.session_state.assumptions.get('opex_percentage', 0.25),
        'total_assets': base_revenue * 0.8,
        'total_liabilities': base_revenue * 0.5,
        'equity': base_revenue * 0.3,
        'current_assets': base_revenue * 0.4,
        'current_liabilities': base_revenue * 0.2,
        'interest_expense': base_revenue * 0.05,
        'long_term_debt': base_revenue * 0.3
    }
    
    if st.button("Generate Projections"):
        with st.spinner("Generating financial projections with loan impact..."):
            # Initialize projections
            projections = FinancialProjections(
                historical_data, 
                st.session_state.assumptions
            )
            
            # Calculate repayment schedule first
            repayment_schedule = projections.calculate_loan_repayment_schedule(
                loan_amount, interest_rate, repayment_period
            )
            st.session_state.repayment_schedule = repayment_schedule
            
            # Generate financial projections with loan impact
            income_projections = projections.project_income_statement(
                periods=projection_years,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                repayment_period=repayment_period
            )
            
            balance_projections = projections.project_balance_sheet(
                income_projections, 
                loan_amount=loan_amount
            )
            
            cashflow_projections = projections.project_cash_flow(
                income_projections, 
                balance_projections, 
                loan_amount=loan_amount,
                repayment_schedule=repayment_schedule
            )
            
            # Calculate DSCR
            dscr_analysis = projections.calculate_debt_service_coverage_ratio(
                income_projections, 
                repayment_schedule
            )
            
            # Store in session state
            st.session_state.income_projections = income_projections
            st.session_state.balance_projections = balance_projections
            st.session_state.cashflow_projections = cashflow_projections
            st.session_state.dscr_analysis = dscr_analysis
    
    # Display projections if available
    if 'income_projections' in st.session_state:
        # Loan Repayment Schedule
        st.header("📅 Loan Repayment Schedule")
        
        if 'repayment_schedule' in st.session_state:
            repayment_display = st.session_state.repayment_schedule.copy()
            repayment_display['payment'] = repayment_display['payment'].apply(lambda x: f"KES {x:,.2f}")
            repayment_display['principal'] = repayment_display['principal'].apply(lambda x: f"KES {x:,.2f}")
            repayment_display['interest'] = repayment_display['interest'].apply(lambda x: f"KES {x:,.2f}")
            repayment_display['remaining_balance'] = repayment_display['remaining_balance'].apply(lambda x: f"KES {x:,.2f}")
            
            st.dataframe(repayment_display, use_container_width=True)
            
            # Repayment schedule chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=st.session_state.repayment_schedule['month'],
                y=st.session_state.repayment_schedule['principal'],
                name='Principal',
                stackgroup='one'
            ))
            fig.add_trace(go.Scatter(
                x=st.session_state.repayment_schedule['month'],
                y=st.session_state.repayment_schedule['interest'],
                name='Interest',
                stackgroup='one'
            ))
            fig.update_layout(
                title='Loan Repayment Schedule (Principal vs Interest)',
                xaxis_title='Month',
                yaxis_title='Amount (KES)',
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Debt Service Coverage Ratio Analysis
        st.header("📊 Debt Service Coverage Ratio (DSCR) Analysis")
        
        if 'dscr_analysis' in st.session_state:
            dscr_display = st.session_state.dscr_analysis.copy()
            dscr_display['ebitda'] = dscr_display['ebitda'].apply(lambda x: f"KES {x:,.0f}")
            dscr_display['total_debt_service'] = dscr_display['total_debt_service'].apply(lambda x: f"KES {x:,.0f}")
            dscr_display['dscr'] = dscr_display['dscr'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(dscr_display, use_container_width=True)
            
            # DSCR trend chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=st.session_state.dscr_analysis['year'],
                y=st.session_state.dscr_analysis['dscr'],
                name='DSCR',
                line=dict(color='#1f77b4', width=3)
            ))
            fig.add_hline(y=1.25, line_dash="dash", line_color="red", annotation_text="Minimum Required DSCR (1.25)")
            fig.add_hline(y=1.5, line_dash="dash", line_color="green", annotation_text="Good DSCR (1.5)")
            fig.update_layout(
                title='Debt Service Coverage Ratio Trend',
                xaxis_title='Year',
                yaxis_title='DSCR',
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.header("💰 Income Statement Projections")
        
        # Format and display income statement
        income_display = st.session_state.income_projections.copy()
        numeric_cols = ['revenue', 'cogs', 'gross_profit', 'operating_expenses', 'ebitda', 'interest_expense', 'ebit', 'tax', 'net_income']
        
        for col in numeric_cols:
            if col in income_display.columns:
                income_display[col] = income_display[col].apply(lambda x: f"KES {x:,.0f}")
        
        st.dataframe(income_display, use_container_width=True)
        
        # Income statement chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=st.session_state.income_projections['year'],
            y=st.session_state.income_projections['revenue'],
            name='Revenue',
            line=dict(color='#1f77b4', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=st.session_state.income_projections['year'],
            y=st.session_state.income_projections['net_income'],
            name='Net Income',
            line=dict(color='#2ca02c', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=st.session_state.income_projections['year'],
            y=st.session_state.income_projections['interest_expense'],
            name='Interest Expense',
            line=dict(color='#ff7f0e', width=3)
        ))
        fig.update_layout(
            title='Revenue, Net Income and Interest Expense Projection',
            xaxis_title='Year',
            yaxis_title='KES',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.header("🏦 Balance Sheet Projections")
        
        # Format and display balance sheet
        balance_display = st.session_state.balance_projections.copy()
        numeric_cols = ['total_assets', 'total_liabilities', 'equity', 'current_assets', 'current_liabilities', 'loan_balance', 'existing_debt']
        
        for col in numeric_cols:
            if col in balance_display.columns:
                balance_display[col] = balance_display[col].apply(lambda x: f"KES {x:,.0f}")
        
        st.dataframe(balance_display, use_container_width=True)
        
        # Balance sheet composition chart
        years = st.session_state.balance_projections['year']
        assets = st.session_state.balance_projections['total_assets']
        liabilities = st.session_state.balance_projections['total_liabilities']
        equity = st.session_state.balance_projections['equity']
        
        fig = go.Figure(data=[
            go.Bar(name='Assets', x=years, y=assets, marker_color='#1f77b4'),
            go.Bar(name='Liabilities', x=years, y=liabilities, marker_color='#ff7f0e'),
            go.Bar(name='Equity', x=years, y=equity, marker_color='#2ca02c')
        ])
        fig.update_layout(
            title='Balance Sheet Composition',
            xaxis_title='Year',
            yaxis_title='KES',
            barmode='group',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.header("💵 Cash Flow Projections")
        
        # Format and display cash flow
        cashflow_display = st.session_state.cashflow_projections.copy()
        numeric_cols = ['operating_cashflow', 'investing_cashflow', 'financing_cashflow', 'net_cashflow']
        
        for col in numeric_cols:
            if col in cashflow_display.columns:
                cashflow_display[col] = cashflow_display[col].apply(lambda x: f"KES {x:,.0f}")
        
        st.dataframe(cashflow_display, use_container_width=True)
        
        # Cash flow chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=st.session_state.cashflow_projections['year'],
            y=st.session_state.cashflow_projections['net_cashflow'],
            name='Net Cash Flow',
            line=dict(color='#17becf', width=3)
        ))
        fig.add_trace(go.Bar(
            x=st.session_state.cashflow_projections['year'],
            y=st.session_state.cashflow_projections['operating_cashflow'],
            name='Operating Cash Flow',
            marker_color='#1f77b4'
        ))
        fig.update_layout(
            title='Cash Flow Projection',
            xaxis_title='Year',
            yaxis_title='KES',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Key metrics summary
        st.header("📈 Key Financial Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            final_revenue = st.session_state.income_projections.iloc[-1]['revenue']
            cagr = Helpers.calculate_growth_rate(
                st.session_state.income_projections.iloc[0]['revenue'],
                final_revenue,
                projection_years
            )
            st.metric("Revenue CAGR", f"{cagr:.1%}")
        
        with col2:
            final_net_income = st.session_state.income_projections.iloc[-1]['net_income']
            avg_margin = st.session_state.income_projections['net_income'].mean() / st.session_state.income_projections['revenue'].mean()
            st.metric("Average Net Margin", f"{avg_margin:.1%}")
        
        with col3:
            total_assets_growth = Helpers.calculate_growth_rate(
                st.session_state.balance_projections.iloc[0]['total_assets'],
                st.session_state.balance_projections.iloc[-1]['total_assets'],
                projection_years
            )
            st.metric("Assets CAGR", f"{total_assets_growth:.1%}")
        
        with col4:
            if 'dscr_analysis' in st.session_state:
                min_dscr = st.session_state.dscr_analysis['dscr'].min()
                st.metric("Minimum DSCR", f"{min_dscr:.2f}", 
                         delta="Adequate" if min_dscr >= 1.25 else "Inadequate")
    
    # Download projections
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Projections Report"):
            st.success("Projections report download initiated")
    
    with col2:
        if st.button("Download Repayment Schedule"):
            st.success("Repayment schedule download initiated")

if __name__ == "__main__":
    main()