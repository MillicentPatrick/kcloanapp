import pandas as pd
import numpy as np
import logging
from utils.file_processing import FileProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.file_processor = FileProcessor()
        
        # Common Kenyan financial statement column mappings
        self.column_mappings = {
            'revenue': ['revenue', 'sales', 'turnover', 'gross revenue', 'total revenue', 'income'],
            'net_income': ['net income', 'net profit', 'profit after tax', 'pat', 'net profit after tax'],
            'total_assets': ['total assets', 'assets', 'non-current assets', 'current assets', 'fixed assets'],
            'total_liabilities': ['total liabilities', 'liabilities', 'non-current liabilities', 'current liabilities'],
            'current_assets': ['current assets', 'inventories', 'receivables', 'cash and cash equivalents'],
            'current_liabilities': ['current liabilities', 'payables', 'short term debt'],
            'equity': ['equity', 'shareholders equity', 'share capital', 'retained earnings'],
            'gross_profit': ['gross profit', 'gross margin'],
            'operating_expenses': ['operating expenses', 'administrative expenses', 'selling expenses'],
            'ebit': ['ebit', 'operating profit', 'profit before interest and tax'],
            'cogs': ['cost of goods sold', 'cogs', 'cost of sales'],
            'cash_flow_operating': ['operating cash flow', 'cash from operations', 'net cash from operating activities'],
            'cash_flow_investing': ['investing cash flow', 'cash from investing activities'],
            'cash_flow_financing': ['financing cash flow', 'cash from financing activities']
        }
    
    def process_uploaded_files(self, uploaded_files):
        """Process multiple uploaded financial files"""
        processed_data = {}
        errors = []
        
        for file in uploaded_files:
            file_type = file.name.split('.')[-1].lower()
            
            try:
                if file_type in ['xlsx', 'xls']:
                    df = self.file_processor.process_excel_file(file)
                    processed_data[file.name] = {
                        'data': df,
                        'type': 'excel',
                        'status': 'success'
                    }
                elif file_type == 'csv':
                    df = self.file_processor.process_csv_file(file)
                    processed_data[file.name] = {
                        'data': df,
                        'type': 'csv', 
                        'status': 'success'
                    }
                elif file_type == 'pdf':
                    data = self.file_processor.extract_financial_data_from_pdf(file)
                    processed_data[file.name] = {
                        'data': data,
                        'type': 'pdf',
                        'status': 'success'
                    }
                else:
                    processed_data[file.name] = {
                        'data': None,
                        'type': file_type,
                        'status': 'error',
                        'error': f'Unsupported file type: {file_type}'
                    }
                    errors.append(f"Unsupported file type: {file_type} for {file.name}")
                    
            except Exception as e:
                error_msg = f"Error processing {file.name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                processed_data[file.name] = {
                    'data': None,
                    'type': file_type,
                    'status': 'error',
                    'error': error_msg
                }
        
        return processed_data, errors
    
    def _map_column_names(self, df):
        """Map various column names to standardized names"""
        df_clean = df.copy()
        df_columns_lower = [str(col).lower().strip() for col in df_clean.columns]
        
        column_mapping = {}
        
        for standard_name, possible_names in self.column_mappings.items():
            for col_name in df_clean.columns:
                col_lower = str(col_name).lower().strip()
                # Check if this column matches any of the possible names
                for possible_name in possible_names:
                    if possible_name in col_lower or col_lower in possible_name:
                        column_mapping[col_name] = standard_name
                        break
        
        # Rename columns
        if column_mapping:
            df_clean = df_clean.rename(columns=column_mapping)
        
        return df_clean
    
    def clean_financial_data(self, df):
        """Clean and standardize financial data"""
        try:
            if df is None or df.empty:
                raise ValueError("DataFrame is empty or None")
            
            # Create a copy to avoid modifying the original
            df_clean = df.copy()
            
            # Remove empty rows and columns
            df_clean = df_clean.dropna(how='all').dropna(axis=1, how='all')
            
            # Reset index after cleaning
            df_clean = df_clean.reset_index(drop=True)
            
            # Map column names to standard names
            df_clean = self._map_column_names(df_clean)
            
            # Convert numeric columns
            numeric_columns = [
                'revenue', 'net_income', 'total_assets', 'total_liabilities',
                'current_assets', 'current_liabilities', 'equity', 'gross_profit',
                'operating_expenses', 'ebit', 'cogs', 'cash_flow_operating',
                'cash_flow_investing', 'cash_flow_financing'
            ]
            
            for col in numeric_columns:
                if col in df_clean.columns:
                    try:
                        # Remove any currency symbols and commas
                        df_clean[col] = df_clean[col].astype(str).str.replace('[₦$£€,]', '', regex=True)
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                        # Fill NaN with 0 for numeric columns
                        df_clean[col] = df_clean[col].fillna(0)
                    except Exception as e:
                        logger.warning(f"Could not convert column {col} to numeric: {e}")
            
            # Remove rows where all numeric values are zero (likely header rows)
            numeric_data = df_clean.select_dtypes(include=[np.number])
            if not numeric_data.empty:
                df_clean = df_clean[(numeric_data != 0).any(axis=1)]
            
            return df_clean
            
        except Exception as e:
            logger.error(f"Error cleaning financial data: {e}")
            raise
    
    def extract_financial_metrics(self, df, statement_type='unknown'):
        """Extract key financial metrics from cleaned data"""
        try:
            metrics = {}
            
            # Get the first row (most recent period) for single-period statements
            # For multi-period statements, take the average or latest based on context
            if len(df) > 1:
                # If there's a date column, use the most recent
                date_columns = [col for col in df.columns if 'date' in str(col).lower() or 'year' in str(col).lower()]
                if date_columns:
                    # Sort by date and take the most recent
                    df_sorted = df.sort_values(by=date_columns[0], ascending=False)
                    latest_row = df_sorted.iloc[0]
                else:
                    # Take the last row assuming it's the most recent
                    latest_row = df.iloc[-1]
            else:
                latest_row = df.iloc[0]
            
            # Extract metrics based on available columns
            for metric in ['revenue', 'net_income', 'total_assets', 'total_liabilities', 
                          'current_assets', 'current_liabilities', 'equity', 'gross_profit',
                          'operating_expenses', 'ebit', 'cogs']:
                if metric in df.columns:
                    value = latest_row[metric]
                    if pd.notna(value) and value != 0:
                        metrics[metric] = float(value)
            
            # Handle statement-specific metrics
            if statement_type == 'income_statement':
                # Calculate derived metrics if possible
                if 'revenue' in metrics and 'cogs' in metrics:
                    metrics['gross_profit'] = metrics['revenue'] - metrics['cogs']
                
                if 'gross_profit' in metrics and 'operating_expenses' in metrics:
                    metrics['ebit'] = metrics['gross_profit'] - metrics['operating_expenses']
            
            elif statement_type == 'balance_sheet':
                # Ensure accounting equation holds
                if 'total_assets' in metrics and 'total_liabilities' in metrics:
                    calculated_equity = metrics['total_assets'] - metrics['total_liabilities']
                    if 'equity' not in metrics or abs(calculated_equity - metrics.get('equity', 0)) > 0.01:
                        metrics['equity'] = calculated_equity
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting financial metrics: {e}")
            return {}
    
    def validate_financial_data(self, df, statement_type='unknown'):
        """Validate financial data for completeness and consistency"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            if df is None or df.empty:
                validation_results['is_valid'] = False
                validation_results['errors'].append("DataFrame is empty or None")
                return validation_results
            
            # Check for required columns based on statement type
            statement_requirements = {
                'income_statement': [['revenue'], ['net_income']],
                'balance_sheet': [['total_assets'], ['total_liabilities']],
                'cash_flow': [['cash_flow_operating']]
            }
            
            df_columns_lower = [str(col).lower() for col in df.columns]
            
            if statement_type in statement_requirements:
                required_groups = statement_requirements[statement_type]
                missing_columns = []
                
                for required_group in required_groups:
                    found = False
                    for required_col in required_group:
                        if required_col in df_columns_lower:
                            found = True
                            break
                    if not found:
                        missing_columns.append(f"one of {required_group}")
                
                if missing_columns:
                    validation_results['warnings'].append(
                        f"Missing recommended columns for {statement_type}: {', '.join(missing_columns)}"
                    )
            else:
                # For unknown type, check for any financial data
                financial_terms = ['revenue', 'income', 'assets', 'liabilities', 'equity', 'profit', 'cash']
                has_financial_data = any(any(term in col for term in financial_terms) for col in df_columns_lower)
                if not has_financial_data:
                    validation_results['warnings'].append("No recognizable financial columns found")
            
            # Check for negative values where not expected (but allow for cash flow statements)
            if statement_type != 'cash_flow':
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if df[col].min() < 0:
                        col_name = str(col)
                        # Some columns can legitimately be negative
                        if not any(term in col_name.lower() for term in ['change', 'flow', 'difference']):
                            validation_results['warnings'].append(f"Column {col} contains negative values")
            
            # Check data consistency for balance sheet
            if statement_type == 'balance_sheet':
                if 'total_assets' in df_columns_lower and 'total_liabilities' in df_columns_lower:
                    assets_col = df.columns[df_columns_lower.index('total_assets')]
                    liabilities_col = df.columns[df_columns_lower.index('total_liabilities')]
                    
                    if (df[assets_col] < df[liabilities_col]).any():
                        validation_results['warnings'].append("Total assets less than total liabilities in some periods")
            
            return validation_results
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
            return validation_results
    
    def detect_financial_statement_type(self, df):
        """Detect the type of financial statement with improved accuracy"""
        try:
            column_names = [str(col).lower() for col in df.columns]
            
            # Income statement indicators
            income_indicators = ['revenue', 'sales', 'cogs', 'gross profit', 'operating income', 'net income', 'ebit', 'ebitda']
            # Balance sheet indicators
            balance_indicators = ['assets', 'liabilities', 'equity', 'current assets', 'fixed assets', 'inventory']
            # Cash flow indicators
            cashflow_indicators = ['operating cash flow', 'investing cash flow', 'financing cash flow', 'cash flow']
            
            income_score = sum(1 for indicator in income_indicators if any(indicator in col for col in column_names))
            balance_score = sum(1 for indicator in balance_indicators if any(indicator in col for col in column_names))
            cashflow_score = sum(1 for indicator in cashflow_indicators if any(indicator in col for col in column_names))
            
            scores = {
                'income_statement': income_score,
                'balance_sheet': balance_score,
                'cash_flow': cashflow_score
            }
            
            # If scores are close, use additional heuristics
            max_score = max(scores.values())
            if max_score > 0:
                # Get all types with max score
                best_types = [stmt_type for stmt_type, score in scores.items() if score == max_score]
                
                if len(best_types) == 1:
                    return best_types[0]
                else:
                    # Tie-breaker: check for specific patterns
                    if any('cash flow' in col for col in column_names):
                        return 'cash_flow'
                    elif any('assets' in col for col in column_names) and any('liabilities' in col for col in column_names):
                        return 'balance_sheet'
                    else:
                        return 'income_statement'
            else:
                return 'unknown'
            
        except Exception as e:
            logger.error(f"Error detecting financial statement type: {e}")
            return 'unknown'