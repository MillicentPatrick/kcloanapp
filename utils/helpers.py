import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

class Helpers:
    @staticmethod
    def format_currency(value):
        """Format value as Kenyan Shillings"""
        return f"KES {value:,.2f}"
    
    @staticmethod
    def calculate_growth_rate(initial, final, periods):
        """Calculate compound annual growth rate"""
        if initial == 0:
            return 0
        return (final / initial) ** (1 / periods) - 1
    
    @staticmethod
    def create_financial_chart(data, chart_type="line", title=""):
        """Create financial charts"""
        if chart_type == "line":
            fig = px.line(data, title=title)
        elif chart_type == "bar":
            fig = px.bar(data, title=title)
        elif chart_type == "pie":
            fig = px.pie(data, title=title)
        
        fig.update_layout(
            template="plotly_white",
            height=400
        )
        return fig
    
    @staticmethod
    def validate_financial_data(df):
        """Validate uploaded financial data"""
        required_columns = ['revenue', 'net_income', 'total_assets', 'total_liabilities']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return True
    
    @staticmethod
    def calculate_loan_affordability(monthly_income, monthly_expenses, existing_debt_payments=0):
        """Calculate loan affordability based on income and expenses"""
        disposable_income = monthly_income - monthly_expenses - existing_debt_payments
        max_affordable_loan_payment = disposable_income * 0.4  # 40% of disposable income
        return max_affordable_loan_payment
    
    @staticmethod
    def format_phone_number(phone):
        """Format Kenyan phone number"""
        phone = str(phone).strip()
        if phone.startswith('0'):
            return '+254' + phone[1:]
        elif phone.startswith('254'):
            return '+' + phone
        else:
            return phone
    
    @staticmethod
    def get_risk_color(risk_level):
        """Get color for risk levels"""
        colors = {
            'Very Low': '#00cc96',
            'Low': '#00cc96', 
            'Medium': '#ffa500',
            'High': '#ff4b4b',
            'Very High': '#8b0000'
        }
        return colors.get(risk_level, '#666666')
