import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import Helpers

def main():
    st.title("📈 Financial Projections Assumptions")
    
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in first")
        return
    
    # Initialize session state for assumptions
    if 'assumptions' not in st.session_state:
        st.session_state.assumptions = {}
    
    st.header("Revenue Growth Assumptions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Revenue Growth (%)")
        revenue_growth = st.slider(
            "Annual Revenue Growth Rate",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=0.5,
            key="revenue_growth"
        )
        st.session_state.assumptions['revenue_growth'] = revenue_growth / 100
    
    with col2:
        st.subheader("Cost Structure")
        cogs_percentage = st.slider(
            "Cost of Goods Sold (% of Revenue)",
            min_value=0.0,
            max_value=100.0,
            value=60.0,
            step=1.0,
            key="cogs_percentage"
        )
        st.session_state.assumptions['cogs_percentage'] = cogs_percentage / 100
        
        opex_percentage = st.slider(
            "Operating Expenses (% of Revenue)",
            min_value=0.0,
            max_value=50.0,
            value=25.0,
            step=1.0,
            key="opex_percentage"
        )
        st.session_state.assumptions['opex_percentage'] = opex_percentage / 100
    
    with col3:
        st.subheader("Tax & Inflation")
        tax_rate = st.slider(
            "Corporate Tax Rate (%)",
            min_value=0.0,
            max_value=40.0,
            value=30.0,
            step=1.0,
            key="tax_rate"
        )
        st.session_state.assumptions['tax_rate'] = tax_rate / 100
        
        inflation_rate = st.slider(
            "Annual Inflation Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=6.5,
            step=0.1,
            key="inflation_rate"
        )
        st.session_state.assumptions['inflation_rate'] = inflation_rate / 100
    
    st.header("Balance Sheet Assumptions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Asset Growth")
        asset_growth = st.slider(
            "Annual Asset Growth Rate (%)",
            min_value=0.0,
            max_value=30.0,
            value=8.0,
            step=0.5,
            key="asset_growth"
        )
        st.session_state.assumptions['asset_growth'] = asset_growth / 100
        
        capex_percentage = st.slider(
            "Capital Expenditure (% of Revenue)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            key="capex_percentage"
        )
        st.session_state.assumptions['capex_percentage'] = capex_percentage / 100
    
    with col2:
        st.subheader("Liability Management")
        debt_growth = st.slider(
            "Debt Growth Rate (%)",
            min_value=-10.0,
            max_value=30.0,
            value=3.0,
            step=0.5,
            key="debt_growth"
        )
        st.session_state.assumptions['debt_growth'] = debt_growth / 100
        
        dividend_payout = st.slider(
            "Dividend Payout Ratio (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=5.0,
            key="dividend_payout"
        )
        st.session_state.assumptions['dividend_payout'] = dividend_payout / 100
    
    with col3:
        st.subheader("Working Capital")
        days_receivable = st.slider(
            "Days Receivable",
            min_value=0,
            max_value=180,
            value=45,
            step=5,
            key="days_receivable"
        )
        st.session_state.assumptions['days_receivable'] = days_receivable
        
        days_payable = st.slider(
            "Days Payable",
            min_value=0,
            max_value=180,
            value=30,
            step=5,
            key="days_payable"
        )
        st.session_state.assumptions['days_payable'] = days_payable
    
    st.header("Industry-Specific Assumptions")
    
    industry = st.selectbox(
        "Select Industry for Benchmarking",
        options=[
            "Agriculture", "Manufacturing", "Building & Construction", 
            "Services", "Trade", "Custom"
        ],
        key="industry_assumptions"
    )
    
    if industry != "Custom":
        # Pre-set industry assumptions
        industry_assumptions = {
            "Agriculture": {
                "revenue_growth": 0.08,
                "cogs_percentage": 0.65,
                "opex_percentage": 0.20
            },
            "Manufacturing": {
                "revenue_growth": 0.12,
                "cogs_percentage": 0.70,
                "opex_percentage": 0.18
            },
            "Building & Construction": {
                "revenue_growth": 0.15,
                "cogs_percentage": 0.75,
                "opex_percentage": 0.15
            },
            "Services": {
                "revenue_growth": 0.10,
                "cogs_percentage": 0.40,
                "opex_percentage": 0.35
            },
            "Trade": {
                "revenue_growth": 0.09,
                "cogs_percentage": 0.80,
                "opex_percentage": 0.12
            }
        }
        
        if st.button(f"Apply {industry} Industry Assumptions"):
            st.session_state.assumptions.update(industry_assumptions[industry])
            st.success(f"{industry} assumptions applied!")
            st.rerun()
    
    st.header("Scenario Analysis")
    
    scenario = st.radio(
        "Select Scenario",
        ["Base Case", "Optimistic", "Pessimistic", "Stress Test"],
        horizontal=True
    )
    
    if scenario == "Optimistic":
        st.session_state.assumptions['revenue_growth'] = st.session_state.assumptions.get('revenue_growth', 0.1) * 1.5
        st.info("Optimistic scenario: Revenue growth increased by 50%")
    elif scenario == "Pessimistic":
        st.session_state.assumptions['revenue_growth'] = st.session_state.assumptions.get('revenue_growth', 0.1) * 0.7
        st.warning("Pessimistic scenario: Revenue growth reduced by 30%")
    elif scenario == "Stress Test":
        st.session_state.assumptions['revenue_growth'] = st.session_state.assumptions.get('revenue_growth', 0.1) * 0.5
        st.session_state.assumptions['cogs_percentage'] = st.session_state.assumptions.get('cogs_percentage', 0.6) * 1.2
        st.error("Stress test: Revenue growth reduced by 50%, COGS increased by 20%")
    
    # Display current assumptions
    st.header("Current Assumptions Summary")
    
    if st.session_state.assumptions:
        assumptions_df = pd.DataFrame.from_dict(
            st.session_state.assumptions, 
            orient='index',
            columns=['Value']
        )
        assumptions_df.index = assumptions_df.index.str.replace('_', ' ').str.title()
        assumptions_df['Value'] = assumptions_df['Value'].apply(
            lambda x: f"{x:.1%}" if isinstance(x, float) and x <= 1 else f"{x:.2f}"
        )
        st.dataframe(assumptions_df, use_container_width=True)
    
    # Download assumptions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Assumptions"):
            st.session_state.saved_assumptions = st.session_state.assumptions.copy()
            st.success("Assumptions saved successfully!")
    
    with col2:
        if st.button("Download Assumptions Report"):
            # Generate PDF report
            st.success("Assumptions report download initiated")

if __name__ == "__main__":
    main()