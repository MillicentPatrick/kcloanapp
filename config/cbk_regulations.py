class CBKRegulations:
    @staticmethod
    def check_single_obligor_limit(loan_amount, core_capital):
        """Check if loan exceeds single obligor limit"""
        return loan_amount <= (core_capital * 0.25)
    
    @staticmethod
    def check_sector_exposure(portfolio_exposure, total_portfolio):
        """Check sector exposure limits"""
        return portfolio_exposure <= (total_portfolio * 0.30)
    
    @staticmethod
    def check_debt_service_ratio(debt_service_ratio):
        """Validate debt service ratio"""
        return debt_service_ratio <= 0.50
    
    @staticmethod
    def check_liquidity_ratio(liquidity_ratio):
        """Validate liquidity ratio"""
        return liquidity_ratio >= 0.20
    
    @staticmethod
    def generate_compliance_report(loan_data):
        """Generate comprehensive compliance report"""
        violations = []
        
        if not CBKRegulations.check_single_obligor_limit(
            loan_data['loan_amount'], loan_data['core_capital']):
            violations.append("Exceeds single obligor limit (25% of core capital)")
            
        if not CBKRegulations.check_debt_service_ratio(
            loan_data.get('debt_service_ratio', 0)):
            violations.append("Debt service ratio exceeds 50%")
            
        return violations