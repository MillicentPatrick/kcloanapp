import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from modules.reporting import PDFReportGenerator
from modules.risk_models import RiskModels
from config.cbk_regulations import CBKRegulations
from modules.projections import FinancialProjections
from utils.helpers import Helpers

def main():
    st.title("📋 Comprehensive Loan Reports")
    
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in first")
        return
    
    st.header("Loan Application Details")
    
    # Client and loan details
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Full Name", key="report_client_name")
        company_name = st.text_input("Company Name", key="report_company_name")
        industry = st.selectbox("Industry", 
                               ["Agriculture", "Manufacturing", "Building & Construction", "Services", "Trade"],
                               key="report_industry")
        business_registration = st.text_input("Business Registration Number")
        years_in_business = st.number_input("Years in Business", min_value=0, max_value=100, value=5)
    
    with col2:
        loan_amount = st.number_input("Loan Amount (KES)", 
                                    min_value=0, 
                                    value=st.session_state.get('loan_amount', 5000000), 
                                    step=100000,
                                    key="report_loan_amount")
        interest_rate = st.number_input("Proposed Interest Rate (%)", 
                                      min_value=0.0, 
                                      max_value=30.0, 
                                      value=st.session_state.get('interest_rate', 12.5),
                                      key="report_interest_rate")
        repayment_period = st.number_input("Repayment Period (Months)", 
                                         min_value=1, 
                                         max_value=120, 
                                         value=st.session_state.get('repayment_period', 36),
                                         key="report_repayment_period")
        loan_purpose = st.text_area("Loan Purpose", "Working capital financing for business expansion")
    
    # Update session state with current loan parameters
    st.session_state.loan_amount = loan_amount
    st.session_state.interest_rate = interest_rate
    st.session_state.repayment_period = repayment_period
    
    # Bank details
    st.header("Bank Processing Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        loan_officer = st.text_input("Loan Officer Name", 
                                   value=st.session_state.user_info.get('role', 'Loan Officer'),
                                   key="report_loan_officer")
        branch = st.text_input("Branch", 
                             value=st.session_state.user_info.get('branch', 'Nairobi Main'),
                             key="report_branch")
        processing_date = st.date_input("Processing Date", datetime.now())
    
    with col2:
        core_capital = st.number_input("Bank Core Capital (KES)", 
                                     min_value=0, 
                                     value=100000000,
                                     key="report_core_capital")
        recommended_decision = st.selectbox("Recommended Decision", 
                                          ["Approve", "Approve with Conditions", "Decline", "Refer to Committee"],
                                          key="report_decision")
        risk_rating = st.select_slider("Risk Rating", 
                                      options=["Very Low", "Low", "Medium", "High", "Very High"],
                                      value="Medium",
                                      key="report_risk_rating")
    
    # Store in session state for report generation
    st.session_state.client_info = {
        'client_name': client_name,
        'company_name': company_name,
        'industry': industry,
        'business_registration': business_registration,
        'years_in_business': years_in_business
    }
    
    st.session_state.bank_info = {
        'loan_officer': loan_officer,
        'branch': branch,
        'processing_date': processing_date,
        'core_capital': core_capital,
        'recommended_decision': recommended_decision,
        'risk_rating': risk_rating
    }
    
    # Risk assessment
    st.header("🛡️ Risk Assessment Summary")
    
    if st.button("Generate Comprehensive Risk Assessment"):
        with st.spinner("Performing comprehensive risk assessment..."):
            # Initialize risk models
            risk_models = RiskModels()
            
            # Calculate Altman Z-Score
            if 'balance_projections' in st.session_state:
                latest_balance = st.session_state.balance_projections.iloc[0]
                working_capital = latest_balance.get('current_assets', 0) - latest_balance.get('current_liabilities', 0)
                retained_earnings = latest_balance.get('equity', 0) * 0.5  # Simplified
                ebit = st.session_state.income_projections.iloc[0].get('ebit', 0)
                
                z_score = risk_models.altman_z_score(
                    working_capital, retained_earnings, ebit,
                    latest_balance.get('equity', 0) * 1.5,  # Market value approximation
                    latest_balance.get('total_assets', 0),
                    latest_balance.get('total_liabilities', 0)
                )
                
                z_zone, z_interpretation = risk_models.interpret_altman_z_score(z_score)
                
                # Machine Learning Credit Score
                if 'financial_analysis' in st.session_state:
                    ml_score = risk_models.machine_learning_credit_scoring(
                        st.session_state.financial_analysis.get('ratios', {})
                    )
                else:
                    ml_score = 75  # Default score
                
                st.session_state.risk_assessment = {
                    'altman_z_score': z_score,
                    'altman_zone': z_zone,
                    'altman_interpretation': z_interpretation,
                    'ml_credit_score': ml_score,
                    'ml_rating': 'Good' if ml_score >= 70 else 'Fair' if ml_score >= 50 else 'Poor'
                }
            
            # CBK Compliance Check
            compliance_data = {
                'loan_amount': loan_amount,
                'core_capital': core_capital,
                'debt_service_ratio': st.session_state.dscr_analysis['dscr'].min() if 'dscr_analysis' in st.session_state else 0.35
            }
            
            violations = CBKRegulations.generate_compliance_report(compliance_data)
            st.session_state.risk_assessment['cbk_violations'] = violations
            st.session_state.risk_assessment['cbk_compliant'] = len(violations) == 0
            
            # Monte Carlo Simulation for cash flow uncertainty
            if 'cashflow_projections' in st.session_state:
                base_cashflow = st.session_state.cashflow_projections['operating_cashflow'].mean()
                simulations = risk_models.monte_carlo_cashflow_simulation(
                    base_cashflow, volatility=0.15, periods=12, simulations=1000
                )
                st.session_state.risk_assessment['cashflow_volatility'] = simulations.std()
    
    # Display risk assessment if available
    if 'risk_assessment' in st.session_state:
        st.subheader("Risk Assessment Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Altman Z-Score", 
                     f"{st.session_state.risk_assessment.get('altman_z_score', 0):.2f}",
                     st.session_state.risk_assessment.get('altman_zone', 'N/A'))
        
        with col2:
            st.metric("ML Credit Score", 
                     f"{st.session_state.risk_assessment.get('ml_credit_score', 0)}/100",
                     st.session_state.risk_assessment.get('ml_rating', 'N/A'))
        
        with col3:
            cbk_status = "Compliant" if st.session_state.risk_assessment.get('cbk_compliant') else "Non-Compliant"
            status_color = "normal" if st.session_state.risk_assessment.get('cbk_compliant') else "off"
            st.metric("CBK Compliance", cbk_status, delta_color=status_color)
        
        with col4:
            if 'dscr_analysis' in st.session_state:
                min_dscr = st.session_state.dscr_analysis['dscr'].min()
                st.metric("Minimum DSCR", f"{min_dscr:.2f}",
                         delta="Adequate" if min_dscr >= 1.25 else "Inadequate")
        
        # Display detailed risk factors
        st.subheader("Detailed Risk Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Financial Risk Factors**")
            if st.session_state.risk_assessment.get('altman_zone') == 'Distress Zone':
                st.error("• High bankruptcy risk (Altman Z-Score in Distress Zone)")
            elif st.session_state.risk_assessment.get('altman_zone') == 'Grey Zone':
                st.warning("• Moderate bankruptcy risk (Altman Z-Score in Grey Zone)")
            else:
                st.success("• Low bankruptcy risk (Altman Z-Score in Safe Zone)")
            
            if st.session_state.risk_assessment.get('ml_credit_score', 0) < 50:
                st.error("• Poor credit score based on ML assessment")
            elif st.session_state.risk_assessment.get('ml_credit_score', 0) < 70:
                st.warning("• Fair credit score based on ML assessment")
            else:
                st.success("• Good credit score based on ML assessment")
        
        with col2:
            st.write("**Compliance & Regulatory Factors**")
            if st.session_state.risk_assessment.get('cbk_violations'):
                st.error("**CBK Compliance Violations:**")
                for violation in st.session_state.risk_assessment['cbk_violations']:
                    st.write(f"• {violation}")
            else:
                st.success("• No CBK compliance violations")
            
            if 'cashflow_volatility' in st.session_state.risk_assessment:
                volatility = st.session_state.risk_assessment['cashflow_volatility']
                if volatility > 0.2:
                    st.warning(f"• High cash flow volatility: {volatility:.1%}")
                else:
                    st.success(f"• Acceptable cash flow volatility: {volatility:.1%}")
    
    # Report generation
    st.header("📄 Report Generation")
    
    report_type = st.radio(
        "Select Report Type",
        ["Executive Summary", "Detailed Analysis", "Credit Committee Package", "Full Loan Package"],
        horizontal=True
    )
    
    # Financial summary for reports
    if 'income_projections' in st.session_state and 'dscr_analysis' in st.session_state:
        st.subheader("Financial Summary for Report")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_revenue = st.session_state.income_projections['revenue'].mean()
            st.metric("Avg Projected Revenue", f"KES {avg_revenue:,.0f}")
        
        with col2:
            avg_net_income = st.session_state.income_projections['net_income'].mean()
            st.metric("Avg Projected Net Income", f"KES {avg_net_income:,.0f}")
        
        with col3:
            min_dscr = st.session_state.dscr_analysis['dscr'].min()
            st.metric("Minimum DSCR", f"{min_dscr:.2f}")
        
        with col4:
            total_interest = st.session_state.repayment_schedule['interest'].sum() if 'repayment_schedule' in st.session_state else 0
            st.metric("Total Interest", f"KES {total_interest:,.0f}")
    
    # Report generation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate PDF Report", type="primary"):
            if not client_name or not company_name:
                st.error("Please fill in client and company details first")
            else:
                with st.spinner("Generating comprehensive PDF report..."):
                    # Prepare data for report
                    loan_data = {
                        'client_name': client_name,
                        'company_name': company_name,
                        'loan_amount': loan_amount,
                        'interest_rate': interest_rate,
                        'repayment_period': repayment_period,
                        'industry': industry,
                        'loan_officer': loan_officer,
                        'branch': branch,
                        'risk_rating': risk_rating,
                        'loan_purpose': loan_purpose,
                        'years_in_business': years_in_business
                    }
                    
                    # Generate PDF report
                    report_generator = PDFReportGenerator()
                    pdf_data = report_generator.create_loan_analysis_report(
                        loan_data,
                        st.session_state.get('financial_analysis', {}),
                        st.session_state.get('risk_assessment', {}),
                        st.session_state.get('income_projections', pd.DataFrame())
                    )
                    
                    # Create download link
                    b64 = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="loan_analysis_report_{company_name.replace(" ", "_")}.pdf">Download PDF Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("PDF report generated successfully!")
    
    with col2:
        if st.button("📋 Generate Executive Summary"):
            st.info("Executive summary generation would be implemented here")
            # This would generate a condensed version of the report
    
    with col3:
        if st.button("📝 Generate Credit Memo"):
            st.info("Credit memo generation would be implemented here")
            # This would generate a formal credit memorandum
    
    # Audit trail and comments
    st.header("📝 Audit Trail & Decision Documentation")
    
    loan_comments = st.text_area(
        "Loan Officer Comments & Analysis", 
        placeholder="Enter your comprehensive analysis, observations, and recommendation rationale...",
        height=150
    )
    
    decision_rationale = st.text_area(
        "Decision Rationale", 
        placeholder="Detailed explanation for the recommended decision...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Comments to Audit Trail"):
            if loan_comments:
                st.session_state.loan_comments = loan_comments
                st.session_state.decision_rationale = decision_rationale
                st.session_state.analysis_timestamp = datetime.now()
                st.success("Comments and rationale saved to audit trail!")
            else:
                st.warning("Please enter comments before saving")
    
    with col2:
        if st.button("🕒 View Audit History"):
            if 'loan_comments' in st.session_state:
                st.write("**Last Saved Analysis:**")
                st.write(f"**Timestamp:** {st.session_state.get('analysis_timestamp', 'N/A')}")
                st.write(f"**Comments:** {st.session_state.loan_comments}")
                st.write(f"**Rationale:** {st.session_state.get('decision_rationale', 'N/A')}")
            else:
                st.info("No audit history found")
    
    # Similar cases analysis
    st.header("🔍 Similar Cases Analysis")
    
    # Display recent decisions (simulated)
    similar_cases = pd.DataFrame({
        'Client': ['Similar Manufacturing Co.', 'Similar Agri Business', 'Similar Construction Ltd'],
        'Industry': [industry, industry, industry],
        'Amount (KES)': [loan_amount * 0.8, loan_amount * 1.2, loan_amount * 0.9],
        'Decision': ['Approved', 'Approved with Conditions', 'Declined'],
        'Risk Rating': ['Medium', 'High', 'Very High'],
        'Current Status': ['Performing', 'Performing', 'N/A'],
        'DSCR': [1.8, 1.3, 0.9]
    })
    
    st.dataframe(similar_cases, use_container_width=True)
    
    # Final approval workflow (for authorized users only)
    user_role = st.session_state.user_info.get('role', '')
    if user_role in ['Branch Manager', 'Risk Manager', 'Admin']:
        st.header("✅ Final Loan Decision")
        
        st.warning("This action will finalize the loan decision and update the system.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approve Loan", type="primary", use_container_width=True):
                st.session_state.final_decision = "APPROVED"
                st.session_state.decision_date = datetime.now()
                st.success("Loan approved successfully!")
                # Here you would typically save to database and trigger next steps
        
        with col2:
            if st.button("⚠️ Approve with Conditions", use_container_width=True):
                st.session_state.final_decision = "APPROVED_WITH_CONDITIONS"
                st.session_state.decision_date = datetime.now()
                conditions = st.text_input("Specify conditions for approval:")
                if conditions:
                    st.session_state.approval_conditions = conditions
                    st.success("Loan approved with conditions!")
        
        with col3:
            if st.button("❌ Decline Loan", use_container_width=True):
                st.session_state.final_decision = "DECLINED"
                st.session_state.decision_date = datetime.now()
                decline_reason = st.text_input("Reason for Decline:")
                if decline_reason:
                    st.session_state.decline_reason = decline_reason
                    st.error("Loan declined!")
    
    # Display final decision if made
    if 'final_decision' in st.session_state:
        st.info(f"**Final Decision:** {st.session_state.final_decision}")
        st.info(f"**Decision Date:** {st.session_state.decision_date}")
        
        if st.session_state.final_decision == "APPROVED_WITH_CONDITIONS" and 'approval_conditions' in st.session_state:
            st.warning(f"**Approval Conditions:** {st.session_state.approval_conditions}")
        elif st.session_state.final_decision == "DECLINED" and 'decline_reason' in st.session_state:
            st.error(f"**Decline Reason:** {st.session_state.decline_reason}")

if __name__ == "__main__":
    main()