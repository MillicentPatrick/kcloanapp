import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
import docx
import io
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileProcessor:
    @staticmethod
    def process_excel_file(uploaded_file):
        """Process uploaded Excel financial statements"""
        try:
            # Read all sheets to find the one with financial data
            excel_file = pd.ExcelFile(uploaded_file)
            sheets = excel_file.sheet_names
            
            # Try to find the most likely sheet with financial data
            financial_sheets = []
            for sheet in sheets:
                df_temp = pd.read_excel(uploaded_file, sheet_name=sheet, nrows=5)
                # Check if this looks like financial data
                if FileProcessor._looks_like_financial_data(df_temp):
                    financial_sheets.append(sheet)
            
            # Use the first financial sheet found, or the first sheet if none identified
            sheet_to_use = financial_sheets[0] if financial_sheets else sheets[0]
            df = pd.read_excel(uploaded_file, sheet_name=sheet_to_use)
            
            logger.info(f"Processed Excel file {uploaded_file.name}, sheet: {sheet_to_use}")
            return df
            
        except Exception as e:
            logger.error(f"Error processing Excel file {uploaded_file.name}: {str(e)}")
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    @staticmethod
    def process_csv_file(uploaded_file):
        """Process uploaded CSV financial statements"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)  # Reset file pointer
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    logger.info(f"Processed CSV file {uploaded_file.name} with encoding: {encoding}")
                    return df
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try with error handling
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='utf-8', errors='ignore')
            logger.warning(f"Processed CSV file {uploaded_file.name} with error handling")
            return df
            
        except Exception as e:
            logger.error(f"Error processing CSV file {uploaded_file.name}: {str(e)}")
            raise Exception(f"Error processing CSV file: {str(e)}")
    
    @staticmethod
    def extract_financial_data_from_pdf(uploaded_file):
        """Extract financial data from PDF statements"""
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Basic financial data extraction (simplified)
            extracted_data = {
                'extracted_text': text[:2000],  # First 2000 characters
                'page_count': len(pdf_reader.pages),
                'financial_terms_found': FileProcessor._extract_financial_terms(text)
            }
            
            logger.info(f"Processed PDF file {uploaded_file.name}, pages: {len(pdf_reader.pages)}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error processing PDF file {uploaded_file.name}: {str(e)}")
            raise Exception(f"Error processing PDF: {str(e)}")
    
    @staticmethod
    def _looks_like_financial_data(df_sample):
        """Check if DataFrame sample looks like financial data"""
        if df_sample is None or df_sample.empty:
            return False
        
        # Check column names for financial terms
        financial_terms = ['revenue', 'income', 'profit', 'assets', 'liabilities', 'equity', 'cash', 'debt']
        columns_lower = [str(col).lower() for col in df_sample.columns]
        
        financial_columns = sum(1 for term in financial_terms if any(term in col for col in columns_lower))
        
        # If at least 2 financial terms found in column names, likely financial data
        return financial_columns >= 2
    
    @staticmethod
    def _detect_kenyan_financial_format(df_sample):
        """Detect common Kenyan financial statement formats"""
        if df_sample is None or df_sample.empty:
            return False
        
        # Check for common Kenyan financial terms
        kenyan_financial_terms = [
            'kra', 'vat', 'paye', 'nssf', 'nhif', 'turnover tax', 'corporation tax',
            'mombasa', 'nairobi', 'kisumu', 'nakuru', 'eldoret'
        ]
        
        columns_text = ' '.join([str(col).lower() for col in df_sample.columns])
        content_text = ' '.join([str(val).lower() for val in df_sample.values.flatten()[:100]])
        all_text = columns_text + ' ' + content_text
        
        kenyan_terms_found = sum(1 for term in kenyan_financial_terms if term in all_text)
        
        return kenyan_terms_found > 0 

    def _extract_financial_terms(text):
        """Extract financial terms from text"""
        financial_terms = [
            'revenue', 'sales', 'income', 'profit', 'loss', 'assets', 'liabilities', 
            'equity', 'cash', 'debt', 'loan', 'interest', 'tax', 'ebitda', 'ebit',
            'current ratio', 'debt to equity', 'return on equity', 'net margin'
        ]
        
        text_lower = text.lower()
        found_terms = [term for term in financial_terms if term in text_lower]
        
        return found_terms