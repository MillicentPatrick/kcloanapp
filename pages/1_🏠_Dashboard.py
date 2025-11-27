import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from modules.auth import Authentication

def main():
    st.title("🏠 Loan Analysis Dashboard")
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in to access the dashboard")
        return
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Loans Processed", "45", "12%")
    with col2:
        st.metric("Approval Rate", "78%", "5%")
    with col3:
        st.metric("Default Rate", "2.3%", "-0.5%")
    with col4:
        st.metric("Portfolio Value", "KES 245M", "8%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Loan distribution by industry
        industry_data = pd.DataFrame({
            'Industry': ['Agriculture', 'Manufacturing', 'Construction', 'Services', 'Trade'],
            'Loans': [15, 12, 8, 6, 4]
        })
        fig = px.pie(industry_data, values='Loans', names='Industry', 
                     title='Loan Distribution by Industry')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk distribution
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Count': [25, 15, 5]
        })
        fig = px.bar(risk_data, x='Risk Level', y='Count',
                     title='Risk Level Distribution', color='Risk Level')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Loan Applications")
    recent_data = pd.DataFrame({
        'Client': ['ABC Manufacturing', 'XYZ Farms', 'Quick Services', 'Build Right Ltd'],
        'Amount (KES)': [5000000, 2500000, 1000000, 7500000],
        'Status': ['Approved', 'Pending', 'Declined', 'Approved'],
        'Risk': ['Low', 'Medium', 'High', 'Medium']
    })
    st.dataframe(recent_data, use_container_width=True)
    
    # Download dashboard report
    if st.button("Download Dashboard Report"):
        # Implementation for PDF generation would go here
        st.success("Dashboard report download initiated")

if __name__ == "__main__":
    main()