import streamlit as st
import pandas as pd
from modules.auth import Authentication

def main():
    st.title("⚙️ Administration Panel")
    
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in first")
        return
    
    # Check if user has admin privileges
    user_role = st.session_state.user_info.get('role', '')
    if user_role not in ['Admin', 'Risk Manager']:
        st.error("Access denied. Admin or Risk Manager privileges required.")
        return
    
    st.header("User Management")
    
    # User management section
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "User Management", 
        "System Configuration", 
        "Audit Logs", 
        "Risk Parameters",
        "Portfolio Analysis"
    ])
    
    with tab1:
        st.subheader("Manage Users")
        
        # Display current users
        auth = Authentication()
        users_df = pd.DataFrame.from_dict(auth.users, orient='index')
        users_df = users_df.reset_index().rename(columns={'index': 'Username'})
        users_df = users_df[['Username', 'role', 'branch']]  # Don't show passwords
        
        st.dataframe(users_df, use_container_width=True)
        
        # Add new user
        st.subheader("Add New User")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
        
        with col2:
            new_role = st.selectbox("Role", 
                                   ["Loan Officer", "Branch Manager", "Risk Manager", "Admin"])
            new_branch = st.text_input("Branch")
        
        with col3:
            if st.button("Create User"):
                if new_username and new_password:
                    # In a real application, you'd add to database
                    st.success(f"User {new_username} created successfully!")
                else:
                    st.error("Please fill all fields")
    
    with tab2:
        st.subheader("System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Maximum Loan Amount (KES)", 
                           min_value=1000000, 
                           max_value=1000000000, 
                           value=50000000,
                           step=1000000)
            
            st.number_input("Minimum Credit Score", 
                           min_value=300, 
                           max_value=850, 
                           value=650)
            
            st.slider("Auto-Approval Threshold", 
                     min_value=0.0, 
                     max_value=1.0, 
                     value=0.8)
        
        with col2:
            st.number_input("Data Retention Period (Months)", 
                           min_value=1, 
                           max_value=120, 
                           value=60)
            
            st.selectbox("Default Currency", 
                        ["KES", "USD", "EUR", "GBP"])
            
            st.text_input("System Contact Email")
        
        if st.button("Save Configuration"):
            st.success("System configuration saved!")
    
    with tab3:
        st.subheader("Audit Logs")
        
        # Simulated audit logs
        audit_data = pd.DataFrame({
            'Timestamp': pd.date_range('2024-01-01', periods=50, freq='D'),
            'User': ['admin', 'loan_officer', 'branch_manager'] * 17,
            'Action': ['Login', 'Loan Review', 'Approval', 'Report Generation'] * 13,
            'Details': ['Successful login', 'Reviewed loan APP001', 'Approved loan APP002', 'Generated report'] * 13,
            'IP Address': ['192.168.1.1', '192.168.1.2', '192.168.1.3'] * 17
        })
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            filter_user = st.multiselect("Filter by User", audit_data['User'].unique())
        
        with col2:
            filter_action = st.multiselect("Filter by Action", audit_data['Action'].unique())
        
        filtered_data = audit_data.copy()
        if filter_user:
            filtered_data = filtered_data[filtered_data['User'].isin(filter_user)]
        if filter_action:
            filtered_data = filtered_data[filtered_data['Action'].isin(filter_action)]
        
        st.dataframe(filtered_data, use_container_width=True)
        
        if st.button("Export Audit Logs"):
            st.success("Audit logs exported successfully!")
    
    with tab4:
        st.subheader("Risk Parameters Configuration")
        
        st.write("**Industry Risk Weights**")
        
        industries = ["Agriculture", "Manufacturing", "Construction", "Services", "Trade"]
        
        for industry in industries:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(industry)
            with col2:
                st.number_input(f"Risk Weight - {industry}", 
                               min_value=0.0, 
                               max_value=1.0, 
                               value=0.7,
                               key=f"risk_weight_{industry}",
                               label_visibility="collapsed")
        
        st.write("**Credit Scoring Parameters**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.number_input("Altman Z-Score Safe Threshold", 
                           min_value=0.0, 
                           max_value=5.0, 
                           value=2.99)
            st.number_input("Minimum Current Ratio", 
                           min_value=0.0, 
                           max_value=5.0, 
                           value=1.5)
        
        with col2:
            st.number_input("Altman Z-Score Grey Threshold", 
                           min_value=0.0, 
                           max_value=5.0, 
                           value=1.81)
            st.number_input("Maximum Debt-to-Equity", 
                           min_value=0.0, 
                           max_value=10.0, 
                           value=2.0)
        
        with col3:
            st.number_input("Probability of Default Threshold", 
                           min_value=0.0, 
                           max_value=1.0, 
                           value=0.1)
            st.number_input("Minimum ROA", 
                           min_value=0.0, 
                           max_value=0.5, 
                           value=0.05)
        
        if st.button("Update Risk Parameters"):
            st.success("Risk parameters updated successfully!")
    
    with tab5:
        st.subheader("Portfolio Analysis")
        
        # Portfolio metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Portfolio", "KES 2.45B", "5.2%")
        with col2:
            st.metric("Non-Performing Loans", "4.3%", "-0.2%")
        with col3:
            st.metric("Average Loan Size", "KES 8.7M", "3.1%")
        with col4:
            st.metric("Portfolio Yield", "14.2%", "0.5%")
        
        # Portfolio concentration
        st.subheader("Portfolio Concentration")
        
        concentration_data = pd.DataFrame({
            'Sector': ['Agriculture', 'Manufacturing', 'Construction', 'Services', 'Trade', 'Other'],
            'Exposure (KES)': [450000000, 600000000, 550000000, 400000000, 350000000, 100000000],
            'Percentage': [18.4, 24.5, 22.4, 16.3, 14.3, 4.1],
            'NPL Rate': [3.2, 2.8, 6.1, 1.9, 4.5, 2.1]
        })
        
        st.dataframe(concentration_data, use_container_width=True)
        
        # CBK compliance monitoring
        st.subheader("CBK Compliance Monitoring")
        
        compliance_data = pd.DataFrame({
            'Requirement': [
                'Single Obligor Limit (25%)',
                'Sector Exposure Limit (30%)', 
                'Capital Adequacy (14%)',
                'Liquidity Ratio (20%)'
            ],
            'Current': [18.2, 24.5, 16.8, 25.3],
            'Required': [25.0, 30.0, 14.0, 20.0],
            'Status': ['Compliant', 'Compliant', 'Compliant', 'Compliant']
        })
        
        st.dataframe(compliance_data, use_container_width=True)
        
        if st.button("Generate Portfolio Report"):
            st.success("Portfolio analysis report generated!")

if __name__ == "__main__":
    main()