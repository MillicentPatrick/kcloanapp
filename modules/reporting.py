from fpdf import FPDF
import pandas as pd
from datetime import datetime

class PDFReportGenerator:
    def __init__(self):
        self.pdf = FPDF()
    
    def create_loan_analysis_report(self, loan_data, financial_analysis, risk_assessment, projections):
        """Create comprehensive PDF report"""
        self.pdf.add_page()
        
        # Header
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'LOAN ANALYSIS REPORT', 0, 1, 'C')
        self.pdf.ln(10)
        
        # Client Information
        self._add_section_header('CLIENT INFORMATION')
        self._add_client_info(loan_data)
        
        # Financial Analysis
        self._add_section_header('FINANCIAL ANALYSIS')
        self._add_financial_analysis(financial_analysis)
        
        # Risk Assessment
        self._add_section_header('RISK ASSESSMENT')
        self._add_risk_assessment(risk_assessment)
        
        # Recommendations
        self._add_section_header('RECOMMENDATIONS')
        self._add_recommendations(loan_data, risk_assessment)
        
        return self.pdf.output(dest='S').encode('latin1')
    
    def _add_section_header(self, title):
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, title, 0, 1)
        self.pdf.set_font('Arial', '', 10)
    
    def _add_client_info(self, loan_data):
        info = [
            f"Client Name: {loan_data.get('client_name', 'N/A')}",
            f"Company: {loan_data.get('company_name', 'N/A')}",
            f"Loan Amount: KES {loan_data.get('loan_amount', 0):,.2f}",
            f"Repayment Period: {loan_data.get('repayment_period', 0)} months",
            f"Industry: {loan_data.get('industry', 'N/A')}",
            f"Loan Officer: {loan_data.get('loan_officer', 'N/A')}",
            f"Branch: {loan_data.get('branch', 'N/A')}"
        ]
        
        for line in info:
            self.pdf.cell(0, 8, line, 0, 1)
        self.pdf.ln(5)
    
    def _add_financial_analysis(self, analysis):
        ratios = analysis.get('ratios', {})
        for ratio, value in ratios.items():
            if isinstance(value, (int, float)):
                self.pdf.cell(0, 8, f"{ratio.replace('_', ' ').title()}: {value:.3f}", 0, 1)
        self.pdf.ln(5)
    
    def _add_risk_assessment(self, assessment):
        self.pdf.cell(0, 8, f"Overall Risk Rating: {assessment.get('risk_rating', 'N/A')}", 0, 1)
        self.pdf.cell(0, 8, f"Altman Z-Score: {assessment.get('altman_z_score', 'N/A')}", 0, 1)
        self.pdf.cell(0, 8, f"Probability of Default: {assessment.get('probability_default', 0):.2%}", 0, 1)
        self.pdf.ln(5)
    
    def _add_recommendations(self, loan_data, risk_assessment):
        risk_rating = risk_assessment.get('risk_rating', 'Medium')
        
        if risk_rating in ['High', 'Very High']:
            recommendation = "DECLINE - High risk identified"
        elif risk_rating == 'Medium':
            recommendation = "APPROVE WITH CONDITIONS - Additional collateral required"
        else:
            recommendation = "APPROVE - Low risk profile"
        
        self.pdf.cell(0, 8, f"Recommendation: {recommendation}", 0, 1)
        
        if risk_assessment.get('violations'):
            self.pdf.cell(0, 8, "CBK Compliance Issues:", 0, 1)
            for violation in risk_assessment['violations']:
                self.pdf.cell(0, 8, f"- {violation}", 0, 1)