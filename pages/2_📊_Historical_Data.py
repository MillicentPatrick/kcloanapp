import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from modules.data_processing import DataProcessor
from modules.financial_analysis import FinancialAnalyzer
from utils.helpers import Helpers
from config.constants import INDUSTRY_CATEGORIES
import io
import base64

def main():
    st.title("📊 Historical Financial Data Analysis")
    
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in first")
        return
    
    # Initialize session state for processed data
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = {}
    if 'financial_metrics' not in st.session_state:
        st.session_state.financial_metrics = {}
    if 'ratio_analysis' not in st.session_state:
        st.session_state.ratio_analysis = {}
    if 'client_info' not in st.session_state:
        st.session_state.client_info = {}
    
    # Client information section
    st.header("👤 Client Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Name", 
                                   value=st.session_state.client_info.get('client_name', ''),
                                   key="historical_client_name")
        company_name = st.text_input("Company Name", 
                                    value=st.session_state.client_info.get('company_name', ''),
                                    key="historical_company_name")
        business_registration = st.text_input("Business Registration Number",
                                             value=st.session_state.client_info.get('business_registration', ''))
        
    with col2:
        industry = st.selectbox("Industry Category", 
                               INDUSTRY_CATEGORIES,
                               index=INDUSTRY_CATEGORIES.index(st.session_state.client_info.get('industry', INDUSTRY_CATEGORIES[0])) if st.session_state.client_info.get('industry') in INDUSTRY_CATEGORIES else 0,
                               key="historical_industry")
        contact_email = st.text_input("Contact Email",
                                     value=st.session_state.client_info.get('contact_email', ''))
        contact_phone = st.text_input("Contact Phone",
                                     value=st.session_state.client_info.get('contact_phone', ''))
        business_age = st.number_input("Years in Business", min_value=0, max_value=100, 
                                      value=st.session_state.client_info.get('business_age', 5))
    
    # Store client info in session state
    st.session_state.client_info = {
        'client_name': client_name,
        'company_name': company_name,
        'industry': industry,
        'business_registration': business_registration,
        'contact_email': contact_email,
        'contact_phone': contact_phone,
        'business_age': business_age
    }
    
    # File upload section
    st.header("📁 Upload Financial Statements")
    
    st.info("""
    **Supported Formats:**
    - Excel files (.xlsx, .xls) - Income statements, balance sheets, cash flow statements
    - CSV files (.csv) - Financial data in tabular format
    - PDF files (.pdf) - Scanned financial statements (basic text extraction)
    """)
    
    uploaded_files = st.file_uploader(
        "Upload financial statements for analysis",
        type=['xlsx', 'xls', 'csv', 'pdf'],
        accept_multiple_files=True,
        help="Upload multiple files for comprehensive analysis"
    )
    
    
    # In the file processing section, update this part:
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
    
        # Process files
        if st.button("🔄 Process Uploaded Files", type="primary"):
             with st.spinner("Processing financial statements..."):
                  processor = DataProcessor()
                  processed_data, errors = processor.process_uploaded_files(uploaded_files)
            
                  # Display any processing errors
                  if errors:
                      for error in errors:
                          st.error(f"❌ {error}")
            
                  # Store processed data
                  st.session_state.processed_data = processed_data
            
                  # Process each file
                  for file_name, file_data in processed_data.items():
                      if file_data['status'] == 'success':
                          st.success(f"✅ Successfully processed: {file_name}")
                    
                          if file_data['type'] in ['excel', 'csv']:
                              df = file_data['data']
                        
                              # Clean and validate data
                              try:
                                  cleaned_data = processor.clean_financial_data(df)
                                  statement_type = processor.detect_financial_statement_type(cleaned_data)
                                  validation = processor.validate_financial_data(cleaned_data, statement_type)
                            
                                  # Display validation results
                                  if not validation['is_valid']:
                                      for error in validation['errors']:
                                          st.error(f"Validation error in {file_name}: {error}")
                                  for warning in validation['warnings']:
                                      st.warning(f"Validation warning in {file_name}: {warning}")
                            
                                  # Extract metrics using the detected statement type
                                  metrics = processor.extract_financial_metrics(cleaned_data, statement_type)
                            
                                  st.session_state.financial_metrics[file_name] = {
                                      'statement_type': statement_type,
                                      'metrics': metrics,
                                      'cleaned_data': cleaned_data
                            }
                            
                                  st.success(f"📊 Detected: {statement_type.replace('_', ' ').title()}")
                            
                                  # Show what columns were found and mapped
                                  with st.expander(f"📋 Column Mapping for {file_name}"):
                                      st.write("**Original Columns:**")
                                      st.write(list(df.columns))
                                      st.write("**Mapped Columns:**")
                                      st.write(list(cleaned_data.columns))
                                      st.write("**Extracted Metrics:**")
                                      st.write(metrics)
                            
                              except Exception as e:
                                  st.error(f"Error processing {file_name}: {str(e)}")
    
    # Display processed data and analysis
    if st.session_state.processed_data:
        st.header("📈 Data Analysis & Results")
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Processed Data", 
            "📊 Financial Metrics", 
            "📐 Ratio Analysis", 
            "📈 Trends & Charts"
        ])
        
        with tab1:
            st.subheader("Processed Financial Data")
            for file_name, file_data in st.session_state.processed_data.items():
                with st.expander(f"📄 {file_name} - {file_data['type'].upper()}"):
                    if file_data['status'] == 'success':
                        if file_data['type'] in ['excel', 'csv']:
                            df = file_data['data']
                            st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                            st.write(f"**Columns:** {', '.join(df.columns.tolist())}")
                            st.dataframe(df.head(10), use_container_width=True)
                            
                            # Show basic statistics for numeric columns
                            numeric_cols = df.select_dtypes(include=[np.number]).columns
                            if len(numeric_cols) > 0:
                                st.subheader("Basic Statistics")
                                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                        else:
                            # PDF data
                            pdf_data = file_data['data']
                            st.text_area("Extracted Text", pdf_data.get('extracted_text', ''), height=200)
                            st.write(f"**Pages:** {pdf_data.get('page_count', 'N/A')}")
                            financial_terms = pdf_data.get('financial_terms_found', [])
                            if financial_terms:
                                st.write(f"**Financial Terms Found:** {', '.join(financial_terms)}")
                    else:
                        st.error(f"Processing failed: {file_data.get('error', 'Unknown error')}")
        
        with tab2:
            st.subheader("Extracted Financial Metrics")
            if st.session_state.financial_metrics:
                for file_name, metrics_data in st.session_state.financial_metrics.items():
                    with st.expander(f"💰 {file_name} - {metrics_data['statement_type'].replace('_', ' ').title()}"):
                        metrics = metrics_data['metrics']
                        
                        if metrics:
                            # Display metrics in a nice format
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if 'revenue' in metrics and metrics['revenue'] > 0:
                                    st.metric("Revenue", Helpers.format_currency(metrics['revenue']))
                                if 'net_income' in metrics:
                                    st.metric("Net Income", Helpers.format_currency(metrics['net_income']))
                            
                            with col2:
                                if 'total_assets' in metrics and metrics['total_assets'] > 0:
                                    st.metric("Total Assets", Helpers.format_currency(metrics['total_assets']))
                                if 'total_liabilities' in metrics:
                                    st.metric("Total Liabilities", Helpers.format_currency(metrics['total_liabilities']))
                            
                            with col3:
                                if 'equity' in metrics:
                                    st.metric("Equity", Helpers.format_currency(metrics['equity']))
                                if 'current_assets' in metrics and 'current_liabilities' in metrics:
                                    if metrics['current_liabilities'] > 0:
                                        current_ratio = metrics['current_assets'] / metrics['current_liabilities']
                                        status = "✅ Good" if current_ratio >= 1.5 else "⚠️ Review" if current_ratio >= 1.0 else "❌ Poor"
                                        st.metric("Current Ratio", f"{current_ratio:.2f}", delta=status)
                            
                            # Detailed metrics table
                            st.subheader("Detailed Metrics")
                            metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
                            metrics_df.index = metrics_df.index.str.replace('_', ' ').str.title()
                            
                            # Format values appropriately
                            def format_metric_value(val):
                                if isinstance(val, (int, float)):
                                    if abs(val) >= 1000:
                                        return Helpers.format_currency(val)
                                    else:
                                        return f"{val:,.2f}"
                                return str(val)
                            
                            metrics_df['Value'] = metrics_df['Value'].apply(format_metric_value)
                            st.dataframe(metrics_df, use_container_width=True)
                        else:
                            st.warning("No financial metrics could be extracted from this file.")
            else:
                st.info("No financial metrics available. Please process the uploaded files first.")
        
        with tab3:
            st.subheader("Financial Ratio Analysis")
            
            if st.session_state.financial_metrics:
                # Perform ratio analysis for each file
                for file_name, metrics_data in st.session_state.financial_metrics.items():
                    with st.expander(f"📐 Ratio Analysis - {file_name}"):
                        metrics = metrics_data['metrics']
                        
                        if metrics:
                            analyzer = FinancialAnalyzer(industry)
                            ratios = analyzer.comprehensive_ratio_analysis(metrics)
                            
                            # Store ratio analysis
                            st.session_state.ratio_analysis[file_name] = ratios
                            
                            # Display key ratios
                            st.subheader("Key Financial Ratios")
                            
                            # Liquidity Ratios
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                current_ratio = ratios.get('current_ratio', 0)
                                status = "✅ Good" if current_ratio >= 1.5 else "⚠️ Review" if current_ratio >= 1.0 else "❌ Poor"
                                st.metric("Current Ratio", f"{current_ratio:.2f}", delta=status)
                            
                            with col2:
                                quick_ratio = ratios.get('quick_ratio', 0)
                                status = "✅ Good" if quick_ratio >= 1.0 else "⚠️ Review" if quick_ratio >= 0.5 else "❌ Poor"
                                st.metric("Quick Ratio", f"{quick_ratio:.2f}", delta=status)
                            
                            with col3:
                                roa = ratios.get('return_on_assets', 0)
                                status = "✅ Good" if roa >= 0.05 else "⚠️ Review" if roa >= 0.02 else "❌ Poor"
                                st.metric("Return on Assets", f"{roa:.1%}", delta=status)
                            
                            with col4:
                                roe = ratios.get('return_on_equity', 0)
                                status = "✅ Good" if roe >= 0.15 else "⚠️ Review" if roe >= 0.08 else "❌ Poor"
                                st.metric("Return on Equity", f"{roe:.1%}", delta=status)
                            
                            # Leverage and Efficiency Ratios
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                debt_to_equity = ratios.get('debt_to_equity', 0)
                                status = "✅ Good" if debt_to_equity <= 2.0 else "⚠️ Review" if debt_to_equity <= 3.0 else "❌ Poor"
                                st.metric("Debt to Equity", f"{debt_to_equity:.2f}", delta=status)
                            
                            with col2:
                                debt_to_assets = ratios.get('debt_to_assets', 0)
                                status = "✅ Good" if debt_to_assets <= 0.6 else "⚠️ Review" if debt_to_assets <= 0.8 else "❌ Poor"
                                st.metric("Debt to Assets", f"{debt_to_assets:.2f}", delta=status)
                            
                            with col3:
                                net_margin = ratios.get('net_profit_margin', 0)
                                status = "✅ Good" if net_margin >= 0.10 else "⚠️ Review" if net_margin >= 0.05 else "❌ Poor"
                                st.metric("Net Profit Margin", f"{net_margin:.1%}", delta=status)
                            
                            with col4:
                                asset_turnover = ratios.get('asset_turnover', 0)
                                status = "✅ Good" if asset_turnover >= 0.5 else "⚠️ Review" if asset_turnover >= 0.3 else "❌ Poor"
                                st.metric("Asset Turnover", f"{asset_turnover:.2f}", delta=status)
                            
                            # Detailed ratio table
                            st.subheader("Comprehensive Ratio Analysis")
                            ratio_df = pd.DataFrame.from_dict(ratios, orient='index', columns=['Value'])
                            ratio_df = ratio_df[~ratio_df.index.isin(['assessment'])]  # Exclude assessment
                            ratio_df.index = ratio_df.index.str.replace('_', ' ').str.title()
                            
                            # Format ratio values
                            def format_ratio_value(val):
                                if isinstance(val, (int, float)):
                                    if any(term in ratio_name.lower() for ratio_name in ratio_df.index for term in ['ratio', 'turnover']):
                                        return f"{val:.3f}"
                                    elif any(term in ratio_name.lower() for ratio_name in ratio_df.index for term in ['return', 'margin']):
                                        return f"{val:.1%}"
                                    else:
                                        return f"{val:.3f}"
                                return str(val)
                            
                            ratio_df['Value'] = ratio_df.apply(
                                lambda row: format_ratio_value(row['Value']), axis=1
                            )
                            st.dataframe(ratio_df, use_container_width=True)
                            
                            # Ratio assessment
                            if 'assessment' in ratios:
                                st.subheader("Ratio Assessment vs Industry Benchmarks")
                                assessment_df = pd.DataFrame.from_dict(ratios['assessment'], orient='index', columns=['Status'])
                                assessment_df.index = assessment_df.index.str.replace('_', ' ').str.title()
                                
                                # Color code the status
                                def color_status(val):
                                    if val == "Within Benchmark":
                                        return "color: green; font-weight: bold;"
                                    elif val == "Below Benchmark":
                                        return "color: orange; font-weight: bold;"
                                    elif val == "Above Benchmark":
                                        return "color: blue; font-weight: bold;"
                                    else:
                                        return ""
                                
                                st.dataframe(assessment_df.style.applymap(color_status), use_container_width=True)
            else:
                st.info("Please process uploaded files to perform ratio analysis.")
        
        with tab4:
            st.subheader("Financial Trends & Visualization")
            
            if st.session_state.financial_metrics:
                # Create visualizations for key metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    # Profitability chart
                    profitability_data = []
                    for file_name, metrics_data in st.session_state.financial_metrics.items():
                        metrics = metrics_data['metrics']
                        if 'revenue' in metrics and 'net_income' in metrics:
                            profitability_data.append({
                                'File': file_name[:30] + '...' if len(file_name) > 30 else file_name,
                                'Revenue': metrics['revenue'],
                                'Net Income': metrics['net_income']
                            })
                    
                    if profitability_data:
                        profit_df = pd.DataFrame(profitability_data)
                        fig = px.bar(profit_df, x='File', y=['Revenue', 'Net Income'],
                                    title='Revenue vs Net Income by File',
                                    barmode='group')
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Balance sheet composition
                    balance_data = []
                    for file_name, metrics_data in st.session_state.financial_metrics.items():
                        metrics = metrics_data['metrics']
                        if 'total_assets' in metrics and 'total_liabilities' in metrics and 'equity' in metrics:
                            balance_data.append({
                                'File': file_name[:30] + '...' if len(file_name) > 30 else file_name,
                                'Assets': metrics['total_assets'],
                                'Liabilities': metrics['total_liabilities'],
                                'Equity': metrics['equity']
                            })
                    
                    if balance_data:
                        balance_df = pd.DataFrame(balance_data)
                        fig = px.bar(balance_df, x='File', y=['Assets', 'Liabilities', 'Equity'],
                                    title='Balance Sheet Composition by File',
                                    barmode='group')
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Ratio comparison across files
                if st.session_state.ratio_analysis:
                    ratio_comparison_data = []
                    for file_name, ratios in st.session_state.ratio_analysis.items():
                        ratio_data = {'File': file_name[:30] + '...' if len(file_name) > 30 else file_name}
                        for ratio_name, value in ratios.items():
                            if ratio_name != 'assessment' and isinstance(value, (int, float)):
                                ratio_data[ratio_name.replace('_', ' ').title()] = value
                        ratio_comparison_data.append(ratio_data)
                    
                    if ratio_comparison_data:
                        ratio_df = pd.DataFrame(ratio_comparison_data)
                        
                        # Select ratios to compare
                        available_ratios = [col for col in ratio_df.columns if col != 'File']
                        if available_ratios:
                            selected_ratios = st.multiselect(
                                "Select ratios to compare across files",
                                options=available_ratios,
                                default=available_ratios[:3] if available_ratios else []
                            )
                            
                            if selected_ratios:
                                fig = px.bar(ratio_df, x='File', y=selected_ratios,
                                            title='Financial Ratios Comparison Across Files',
                                            barmode='group')
                                fig.update_layout(xaxis_tickangle=-45)
                                st.plotly_chart(fig, use_container_width=True)
    
    # Download section
    st.header("📥 Download Analysis Reports")
    
    if st.session_state.financial_metrics:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download Financial Metrics Report"):
                # Create a comprehensive report
                metrics_list = []
                for file_name, metrics_data in st.session_state.financial_metrics.items():
                    for metric, value in metrics_data['metrics'].items():
                        metrics_list.append({
                            'File': file_name,
                            'Metric': metric.replace('_', ' ').title(),
                            'Value': value,
                            'Statement Type': metrics_data['statement_type'].replace('_', ' ').title()
                        })
                
                if metrics_list:
                    metrics_df = pd.DataFrame(metrics_list)
                    csv = metrics_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="financial_metrics_report.csv">Download CSV Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Financial metrics report generated!")
        
        with col2:
            if st.button("📐 Download Ratio Analysis Report"):
                if st.session_state.ratio_analysis:
                    ratio_list = []
                    for file_name, ratios in st.session_state.ratio_analysis.items():
                        for ratio_name, value in ratios.items():
                            if ratio_name != 'assessment':
                                ratio_list.append({
                                    'File': file_name,
                                    'Ratio': ratio_name.replace('_', ' ').title(),
                                    'Value': value
                                })
                    
                    if ratio_list:
                        ratio_df = pd.DataFrame(ratio_list)
                        csv = ratio_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="ratio_analysis_report.csv">Download CSV Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.success("Ratio analysis report generated!")
        
        with col3:
            if st.button("📋 Generate Comprehensive PDF Report"):
                st.info("Comprehensive PDF report generation would be implemented here")
                st.success("This would generate a complete PDF report with all analysis, charts, and recommendations")

    # Clear data button
    if st.session_state.processed_data:
        st.markdown("---")
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state.processed_data = {}
            st.session_state.financial_metrics = {}
            st.session_state.ratio_analysis = {}
            st.session_state.client_info = {}
            st.rerun()

if __name__ == "__main__":
    main()