import pandas as pd
import numpy as np
from config.constants import INDUSTRY_BENCHMARKS

class FinancialAnalyzer:
    def __init__(self, industry_category):
        self.industry_category = industry_category
    
    def calculate_liquidity_ratios(self, current_assets, current_liabilities):
        """Calculate liquidity ratios"""
        if current_liabilities == 0:
            return {"current_ratio": 0, "quick_ratio": 0}
        
        current_ratio = current_assets / current_liabilities
        quick_ratio = (current_assets) / current_liabilities  # Simplified
        
        return {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio
        }
    
    def calculate_profitability_ratios(self, revenue, net_income, total_assets, equity):
        """Calculate profitability ratios"""
        roa = net_income / total_assets if total_assets > 0 else 0
        roe = net_income / equity if equity > 0 else 0
        net_margin = net_income / revenue if revenue > 0 else 0
        
        return {
            "return_on_assets": roa,
            "return_on_equity": roe,
            "net_profit_margin": net_margin
        }
    
    def calculate_leverage_ratios(self, total_liabilities, total_assets, equity):
        """Calculate leverage ratios"""
        debt_to_equity = total_liabilities / equity if equity > 0 else 0
        debt_to_assets = total_liabilities / total_assets if total_assets > 0 else 0
        
        return {
            "debt_to_equity": debt_to_equity,
            "debt_to_assets": debt_to_assets
        }
    
    def calculate_efficiency_ratios(self, revenue, total_assets, accounts_receivable):
        """Calculate efficiency ratios"""
        asset_turnover = revenue / total_assets if total_assets > 0 else 0
        receivables_turnover = revenue / accounts_receivable if accounts_receivable > 0 else 0
        
        return {
            "asset_turnover": asset_turnover,
            "receivables_turnover": receivables_turnover
        }
    
    def comprehensive_ratio_analysis(self, financial_data):
        """Perform comprehensive ratio analysis"""
        ratios = {}
        
        # Liquidity ratios
        ratios.update(self.calculate_liquidity_ratios(
            financial_data.get('current_assets', 0),
            financial_data.get('current_liabilities', 0)
        ))
        
        # Profitability ratios
        ratios.update(self.calculate_profitability_ratios(
            financial_data.get('revenue', 0),
            financial_data.get('net_income', 0),
            financial_data.get('total_assets', 0),
            financial_data.get('equity', 0)
        ))
        
        # Leverage ratios
        ratios.update(self.calculate_leverage_ratios(
            financial_data.get('total_liabilities', 0),
            financial_data.get('total_assets', 0),
            financial_data.get('equity', 0)
        ))
        
        # Efficiency ratios
        ratios.update(self.calculate_efficiency_ratios(
            financial_data.get('revenue', 0),
            financial_data.get('total_assets', 0),
            financial_data.get('accounts_receivable', 0)
        ))
        
        # Assess against benchmarks
        ratios['assessment'] = self.assess_against_benchmarks(ratios)
        
        return ratios
    
    def assess_against_benchmarks(self, ratios):
        """Assess ratios against industry benchmarks"""
        assessment = {}
        
        for ratio, value in ratios.items():
            if ratio in INDUSTRY_BENCHMARKS:
                benchmark = INDUSTRY_BENCHMARKS[ratio]
                if value < benchmark.get('min', 0):
                    assessment[ratio] = "Below Benchmark"
                elif value > benchmark.get('max', float('inf')):
                    assessment[ratio] = "Above Benchmark"
                else:
                    assessment[ratio] = "Within Benchmark"
            else:
                assessment[ratio] = "No Benchmark"
        
        return assessment