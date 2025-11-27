import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from modules.financial_analysis import FinancialAnalyzer
from config.constants import INDUSTRY_BENCHMARKS

def main():
    st.title("📐 Financial Ratio Analysis")
    
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in first")
        return
    
    # Check if projections are available
    if 'income_projections' not in st.session_state:
        st.error("Please generate projections first on the Projections page")
        return
    
    st.header("Comprehensive Ratio Analysis")
    
    # Calculate ratios for each projection year
    ratios_data = []
    
    for idx, (income_row, balance_row) in enumerate(zip(
        st.session_state.income_projections.iterrows(),
        st.session_state.balance_projections.iterrows())):
        
        year_data = income_row[1].to_dict()
        year_data.update(balance_row[1].to_dict())
        
        analyzer = FinancialAnalyzer("General")
        ratios = analyzer.comprehensive_ratio_analysis(year_data)
        ratios['year'] = year_data['year']
        
        ratios_data.append(ratios)
    
    ratios_df = pd.DataFrame(ratios_data)
    
    # Display ratio analysis
    st.subheader("Ratio Trends Over Time")
    
    # Select ratios to display
    available_ratios = [col for col in ratios_df.columns if col not in ['year', 'assessment']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        ratio_1 = st.selectbox(
            "Select Ratio 1",
            options=available_ratios,
            index=0,
            key="ratio_1"
        )
    
    with col2:
        ratio_2 = st.selectbox(
            "Select Ratio 2", 
            options=available_ratios,
            index=1,
            key="ratio_2"
        )
    
    # Ratio trends chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=ratios_df['year'],
        y=ratios_df[ratio_1],
        name=ratio_1.replace('_', ' ').title(),
        line=dict(width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=ratios_df['year'],
        y=ratios_df[ratio_2],
        name=ratio_2.replace('_', ' ').title(),
        line=dict(width=3)
    ))
    
    fig.update_layout(
        title=f'{ratio_1.replace("_", " ").title()} vs {ratio_2.replace("_", " ").title()}',
        xaxis_title='Year',
        yaxis_title='Ratio Value',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed ratio analysis
    st.subheader("Detailed Ratio Analysis")
    
    # Liquidity Ratios
    st.write("**Liquidity Ratios**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_ratio = ratios_df['current_ratio'].iloc[-1]
        benchmark = INDUSTRY_BENCHMARKS['current_ratio']
        status = "✅ Good" if benchmark['min'] <= current_ratio <= benchmark['max'] else "⚠️ Review"
        st.metric("Current Ratio", f"{current_ratio:.2f}", delta=status)
    
    with col2:
        quick_ratio = ratios_df['quick_ratio'].iloc[-1]
        status = "✅ Good" if quick_ratio >= 1.0 else "⚠️ Review" if quick_ratio >= 0.5 else "❌ Poor"
        st.metric("Quick Ratio", f"{quick_ratio:.2f}", delta=status)
    
    # Profitability Ratios
    st.write("**Profitability Ratios**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        roa = ratios_df['return_on_assets'].iloc[-1]
        benchmark = INDUSTRY_BENCHMARKS['roa']
        status = "✅ Good" if roa >= benchmark['min'] else "⚠️ Review"
        st.metric("Return on Assets", f"{roa:.1%}", delta=status)
    
    with col2:
        roe = ratios_df['return_on_equity'].iloc[-1]
        benchmark = INDUSTRY_BENCHMARKS['roe']
        status = "✅ Good" if roe >= benchmark['min'] else "⚠️ Review"
        st.metric("Return on Equity", f"{roe:.1%}", delta=status)
    
    with col3:
        net_margin = ratios_df['net_profit_margin'].iloc[-1]
        status = "✅ Good" if net_margin >= 0.10 else "⚠️ Review" if net_margin >= 0.05 else "❌ Poor"
        st.metric("Net Profit Margin", f"{net_margin:.1%}", delta=status)
    
    # Leverage Ratios
    st.write("**Leverage Ratios**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        debt_to_equity = ratios_df['debt_to_equity'].iloc[-1]
        benchmark = INDUSTRY_BENCHMARKS['debt_to_equity']
        status = "✅ Good" if benchmark['min'] <= debt_to_equity <= benchmark['max'] else "⚠️ Review"
        st.metric("Debt to Equity", f"{debt_to_equity:.2f}", delta=status)
    
    with col2:
        debt_to_assets = ratios_df['debt_to_assets'].iloc[-1]
        status = "✅ Good" if debt_to_assets <= 0.6 else "⚠️ Review" if debt_to_assets <= 0.8 else "❌ Poor"
        st.metric("Debt to Assets", f"{debt_to_assets:.2f}", delta=status)
    
    # Efficiency Ratios - FIXED SECTION
    st.write("**Efficiency Ratios**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        asset_turnover = ratios_df['asset_turnover'].iloc[-1]
        status = "✅ Good" if asset_turnover >= 0.5 else "⚠️ Review" if asset_turnover >= 0.3 else "❌ Poor"
        st.metric("Asset Turnover", f"{asset_turnover:.2f}", delta=status)
    
    with col2:
        # FIX: Check if receivables_turnover column exists and has values
        if 'receivables_turnover' in ratios_df.columns and not ratios_df['receivables_turnover'].isna().iloc[-1]:
            receivables_turnover_value = ratios_df['receivables_turnover'].iloc[-1]
            status = "✅ Good" if receivables_turnover_value >= 6.0 else "⚠️ Review" if receivables_turnover_value >= 4.0 else "❌ Poor"
            st.metric("Receivables Turnover", f"{receivables_turnover_value:.2f}", delta=status)
    
    # Ratio heatmap
    st.subheader("Ratio Performance Heatmap")
    
    # Prepare data for heatmap
    heatmap_data = []
    for ratio in available_ratios:
        current_value = ratios_df[ratio].iloc[-1]
        
        if ratio in INDUSTRY_BENCHMARKS:
            benchmark = INDUSTRY_BENCHMARKS[ratio]
            if 'min' in benchmark and 'max' in benchmark:
                if current_value < benchmark['min']:
                    status = -1  # Below benchmark
                elif current_value > benchmark['max']:
                    status = 1   # Above benchmark
                else:
                    status = 0   # Within benchmark
            elif 'min' in benchmark:
                status = 1 if current_value >= benchmark['min'] else -1
            else:
                status = 0
        else:
            status = 0
        
        heatmap_data.append({
            'Ratio': ratio.replace('_', ' ').title(),
            'Current Value': current_value,
            'Status': status
        })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Create heatmap
    fig = px.imshow(
        heatmap_df[['Status']].T,
        x=heatmap_df['Ratio'],
        y=['Performance'],
        color_continuous_scale=['red', 'yellow', 'green'],
        aspect="auto"
    )
    
    fig.update_layout(
        title="Ratio Performance vs Industry Benchmarks",
        xaxis_title="Ratios",
        height=200
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed ratio table
    st.subheader("Detailed Ratio Analysis Table")
    
    display_ratios = ratios_df.copy()
    for col in available_ratios:
        if col in display_ratios.columns and display_ratios[col].dtype in ['float64', 'int64']:
            display_ratios[col] = display_ratios[col].apply(lambda x: f"{x:.3f}")
    
    st.dataframe(display_ratios, use_container_width=True)
    
    # Risk assessment based on ratios
    st.header("Risk Assessment")
    
    high_risk_factors = []
    medium_risk_factors = []
    
    # Get latest values for cleaner code
    latest_current_ratio = ratios_df['current_ratio'].iloc[-1]
    latest_debt_to_equity = ratios_df['debt_to_equity'].iloc[-1]
    latest_roa = ratios_df['return_on_assets'].iloc[-1]
    latest_quick_ratio = ratios_df['quick_ratio'].iloc[-1]
    latest_net_margin = ratios_df['net_profit_margin'].iloc[-1]
    
    # Check various risk factors
    if latest_current_ratio < 1.0:
        high_risk_factors.append("Current ratio below 1.0 - Liquidity concern")
    elif latest_current_ratio < 1.5:
        medium_risk_factors.append("Current ratio below 1.5 - Monitor liquidity")
    
    if latest_debt_to_equity > 2.0:
        high_risk_factors.append("Debt-to-equity above 2.0 - High leverage")
    elif latest_debt_to_equity > 1.5:
        medium_risk_factors.append("Debt-to-equity above 1.5 - Moderate leverage")
    
    if latest_roa < 0.02:
        high_risk_factors.append("ROA below 2% - Poor asset utilization")
    elif latest_roa < 0.05:
        medium_risk_factors.append("ROA below 5% - Below average performance")
    
    if latest_quick_ratio < 0.5:
        high_risk_factors.append("Quick ratio below 0.5 - Immediate liquidity risk")
    elif latest_quick_ratio < 1.0:
        medium_risk_factors.append("Quick ratio below 1.0 - Limited liquid assets")
    
    if latest_net_margin < 0.02:
        high_risk_factors.append("Net profit margin below 2% - Profitability concern")
    elif latest_net_margin < 0.05:
        medium_risk_factors.append("Net profit margin below 5% - Low profitability")
    
    # Display risk factors
    col1, col2 = st.columns(2)
    
    with col1:
        if high_risk_factors:
            st.error("**High Risk Factors**")
            for factor in high_risk_factors:
                st.write(f"• {factor}")
        else:
            st.success("**No High Risk Factors**")
    
    with col2:
        if medium_risk_factors:
            st.warning("**Medium Risk Factors**")
            for factor in medium_risk_factors:
                st.write(f"• {factor}")
        else:
            st.success("**No Medium Risk Factors**")
    
    if not high_risk_factors and not medium_risk_factors:
        st.success("**Excellent Financial Health** - No significant risk factors identified")
    
    # Additional insights
    st.header("Financial Insights")
    
    insights = []
    
    # Generate insights based on ratios
    if latest_current_ratio > 3.0:
        insights.append("**High liquidity** - Consider optimizing working capital management")
    
    if latest_debt_to_equity < 0.5:
        insights.append("**Conservative leverage** - Potential capacity for strategic borrowing")
    
    if latest_roa > 0.10:
        insights.append("**Strong asset efficiency** - Excellent returns on asset investments")
    
    if latest_net_margin > 0.15:
        insights.append("**High profitability** - Strong competitive position and cost control")
    
    if insights:
        st.info("**Key Insights:**")
        for insight in insights:
            st.write(f"• {insight}")
    
    # Download ratios report
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Ratio Analysis Report"):
            # Create downloadable CSV
            csv = ratios_df.to_csv(index=False)
            st.download_button(
                label="Download CSV Report",
                data=csv,
                file_name="ratio_analysis_report.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Download Risk Assessment"):
            # Create risk assessment report
            risk_report = {
                'Assessment Date': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
                'High Risk Factors Count': [len(high_risk_factors)],
                'Medium Risk Factors Count': [len(medium_risk_factors)],
                'Overall Risk Level': ['High' if high_risk_factors else 'Medium' if medium_risk_factors else 'Low']
            }
            
            risk_df = pd.DataFrame(risk_report)
            
            # Add detailed factors
            details_df = pd.DataFrame({
                'Risk Level': ['High'] * len(high_risk_factors) + ['Medium'] * len(medium_risk_factors),
                'Factors': high_risk_factors + medium_risk_factors
            })
            
            # Combine reports
            combined_report = pd.concat([risk_df, details_df], axis=1)
            csv = combined_report.to_csv(index=False)
            
            st.download_button(
                label="Download Risk Report",
                data=csv,
                file_name="risk_assessment_report.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()