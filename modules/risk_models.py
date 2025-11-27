import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class RiskModels:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def altman_z_score(self, working_capital, retained_earnings, ebit, 
                      market_value_equity, total_assets, total_liabilities):
        """Calculate Altman Z-Score for bankruptcy prediction"""
        if total_assets == 0:
            return 0
        
        X1 = working_capital / total_assets
        X2 = retained_earnings / total_assets
        X3 = ebit / total_assets
        X4 = market_value_equity / total_liabilities if total_liabilities > 0 else 0
        X5 = total_assets  # Sales/Total Assets simplified
        
        z_score = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
        
        return z_score
    
    def interpret_altman_z_score(self, z_score):
        """Interpret Altman Z-Score"""
        if z_score > 2.99:
            return "Safe Zone", "Low bankruptcy risk"
        elif z_score > 1.81:
            return "Grey Zone", "Moderate bankruptcy risk"
        else:
            return "Distress Zone", "High bankruptcy risk"
    
    def merton_structural_model(self, company_value, debt_face_value, risk_free_rate, 
                               volatility, time_to_maturity=1):
        """Merton structural credit risk model"""
        try:
            d1 = (np.log(company_value / debt_face_value) + 
                 (risk_free_rate + 0.5 * volatility**2) * time_to_maturity) / \
                 (volatility * np.sqrt(time_to_maturity))
            d2 = d1 - volatility * np.sqrt(time_to_maturity)
            
            probability_default = stats.norm.cdf(-d2)
            distance_to_default = d2
            
            return probability_default, distance_to_default
        except:
            return 0.5, 0  # Default values in case of error
    
    def monte_carlo_cashflow_simulation(self, base_cashflow, volatility, periods=12, simulations=1000):
        """Monte Carlo simulation for cash flow uncertainty"""
        np.random.seed(42)
        
        simulations_data = np.zeros((periods, simulations))
        current_cashflow = base_cashflow
        
        for t in range(periods):
            random_shocks = np.random.normal(0, volatility, simulations)
            simulated_cashflows = current_cashflow * (1 + random_shocks)
            simulations_data[t] = simulated_cashflows
            current_cashflow = np.mean(simulated_cashflows)
        
        return simulations_data
    
    def machine_learning_credit_scoring(self, financial_ratios, historical_data=None):
        """Machine learning based credit scoring"""
        # Simplified implementation - in practice, you'd train on historical data
        features = np.array([[
            financial_ratios.get('current_ratio', 0),
            financial_ratios.get('debt_to_equity', 0),
            financial_ratios.get('return_on_assets', 0),
            financial_ratios.get('net_profit_margin', 0)
        ]])
        
        # Simple rule-based scoring (replace with trained model)
        score = 0
        if financial_ratios.get('current_ratio', 0) > 1.5:
            score += 25
        if financial_ratios.get('debt_to_equity', 0) < 2.0:
            score += 25
        if financial_ratios.get('return_on_assets', 0) > 0.05:
            score += 25
        if financial_ratios.get('net_profit_margin', 0) > 0.1:
            score += 25
        
        return min(score, 100)