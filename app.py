import streamlit as st
import pandas as pd
import io
import zipfile
import base64
from datetime import datetime
import os
import sys
import traceback
from pathlib import Path

# Import custom utilities
from utils.excel_processor import ExcelProcessor
from utils.report_generator import ReportGenerator
from utils.pdf_generator import PDFGenerator
from utils.template_renderer import TemplateRenderer

class BillGeneratorApp:
    """Main application class for the Bill Generator"""
    
    def __init__(self):
        self.excel_processor = ExcelProcessor()
        self.report_generator = ReportGenerator()
        self.pdf_generator = PDFGenerator()
        self.template_renderer = TemplateRenderer()
        
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Professional Bill Generator",
            page_icon="🧾",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def load_custom_css(self):
        """Load custom CSS and JavaScript for balloon animation"""
        css_file = Path("assets/style.css")
        js_file = Path("assets/balloon.js")
        
        if css_file.exists():
            with open(css_file) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
        if js_file.exists():
            with open(js_file) as f:
                st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)
    
    def render_header(self):
        """Render application header with logo and balloon animation"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class="header-container">
                <h1 class="main-title">🧾 Professional Bill Generator</h1>
                <div class="balloon-container">
                    <div class="balloon balloon1">🎈</div>
                    <div class="balloon balloon2">🎈</div>
                    <div class="balloon balloon3">🎈</div>
                </div>
                <p class="subtitle">An Initiative by Mrs. Premlata Jain, Additional Administrative Officer, PWD, Udaipur</p>
                <div class="wishes-message">
                    <p>✨ Best Wishes for Professional Excellence ✨</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def process_files(self, uploaded_files):
        """Process multiple Excel files and generate reports"""
        if not uploaded_files:
            st.warning("Please upload at least one Excel file.")
            return
        
        if len(uploaded_files) > 10:
            st.error("Maximum 10 files can be processed simultaneously.")
            return
        
        # Check file sizes
        for uploaded_file in uploaded_files:
            if uploaded_file.size > 50 * 1024 * 1024:  # 50MB limit
                st.error(f"File {uploaded_file.name} is too large. Maximum size is 50MB.")
                return
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_outputs = {}
        
        for idx, uploaded_file in enumerate(uploaded_files):
            try:
                # Update progress
                progress = (idx + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Process Excel file
                file_data = self.excel_processor.process_excel_file(uploaded_file)
                
                if file_data:
                    # Generate reports
                    reports = self.report_generator.generate_all_reports(file_data)
                    
                    # Create file outputs
                    file_outputs = self.create_file_outputs(reports, uploaded_file.name)
                    all_outputs[uploaded_file.name] = file_outputs
                    
                    st.success(f"✅ Successfully processed {uploaded_file.name}")
                else:
                    st.error(f"❌ Failed to process {uploaded_file.name}")
                    
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                st.error(traceback.format_exc())
        
        progress_bar.progress(1.0)
        status_text.text("Processing complete!")
        
        if all_outputs:
            self.provide_download_options(all_outputs)
    
    def create_file_outputs(self, reports, filename):
        """Create downloadable outputs for a single file"""
        outputs = {}
        
        # Generate PDFs
        outputs['first_page.pdf'] = self.pdf_generator.generate_pdf(
            reports['first_page_html'], 'first_page'
        )
        outputs['deviation_statement.pdf'] = self.pdf_generator.generate_pdf(
            reports['deviation_statement_html'], 'deviation_statement'
        )
        outputs['note_sheet.pdf'] = self.pdf_generator.generate_pdf(
            reports['note_sheet_html'], 'note_sheet'
        )
        outputs['certificate_ii.pdf'] = self.pdf_generator.generate_pdf(
            reports['certificate_ii_html'], 'certificate_ii'
        )
        outputs['certificate_iii.pdf'] = self.pdf_generator.generate_pdf(
            reports['certificate_iii_html'], 'certificate_iii'
        )
        
        if reports.get('extra_items_html'):
            outputs['extra_items.pdf'] = self.pdf_generator.generate_pdf(
                reports['extra_items_html'], 'extra_items'
            )
        
        # Generate combined PDF
        outputs['combined_report.pdf'] = self.pdf_generator.create_combined_pdf([
            outputs['first_page.pdf'],
            outputs['deviation_statement.pdf'],
            outputs['note_sheet.pdf'],
            outputs['certificate_ii.pdf'],
            outputs['certificate_iii.pdf']
        ] + ([outputs['extra_items.pdf']] if 'extra_items.pdf' in outputs else []))
        
        # Generate HTML files
        outputs['first_page.html'] = reports['first_page_html'].encode()
        outputs['deviation_statement.html'] = reports['deviation_statement_html'].encode()
        outputs['note_sheet.html'] = reports['note_sheet_html'].encode()
        outputs['certificate_ii.html'] = reports['certificate_ii_html'].encode()
        outputs['certificate_iii.html'] = reports['certificate_iii_html'].encode()
        
        if reports.get('extra_items_html'):
            outputs['extra_items.html'] = reports['extra_items_html'].encode()
        
        # Generate DOCX files (simplified implementation)
        # Note: Full DOCX generation would require python-docx library
        outputs['summary.txt'] = self.create_summary_text(reports).encode()
        
        return outputs
    
    def create_summary_text(self, reports):
        """Create a text summary of the reports"""
        summary = f"""
BILL PROCESSING SUMMARY
Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Reports Generated:
- First Page Report
- Deviation Statement
- Note Sheet
- Certificate II
- Certificate III
"""
        if reports.get('extra_items_html'):
            summary += "- Extra Items Report\n"
        
        summary += "\nAll reports have been generated successfully with proper formatting and calculations."
        
        return summary
    
    def provide_download_options(self, all_outputs):
        """Provide download options for all processed files"""
        st.markdown("---")
        st.header("📥 Download Reports")
        
        # Create master ZIP file
        master_zip = io.BytesIO()
        with zipfile.ZipFile(master_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, outputs in all_outputs.items():
                # Create individual ZIP for each file
                file_zip = io.BytesIO()
                with zipfile.ZipFile(file_zip, 'w', zipfile.ZIP_DEFLATED) as file_zf:
                    for output_name, output_data in outputs.items():
                        file_zf.writestr(output_name, output_data)
                
                # Add individual ZIP to master ZIP
                clean_filename = filename.replace('.xlsx', '').replace('.xls', '')
                zf.writestr(f"{clean_filename}_reports.zip", file_zip.getvalue())
        
        master_zip.seek(0)
        
        # Provide master download
        st.download_button(
            label="📦 Download All Reports (ZIP)",
            data=master_zip.getvalue(),
            file_name=f"bill_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
        
        # Individual file downloads
        for filename, outputs in all_outputs.items():
            with st.expander(f"📄 {filename} - Individual Downloads"):
                cols = st.columns(3)
                col_idx = 0
                
                for output_name, output_data in outputs.items():
                    with cols[col_idx % 3]:
                        mime_type = self.get_mime_type(output_name)
                        st.download_button(
                            label=f"⬇️ {output_name}",
                            data=output_data,
                            file_name=output_name,
                            mime=mime_type
                        )
                    col_idx += 1
    
    def get_mime_type(self, filename):
        """Get appropriate MIME type for file"""
        if filename.endswith('.pdf'):
            return "application/pdf"
        elif filename.endswith('.html'):
            return "text/html"
        elif filename.endswith('.txt'):
            return "text/plain"
        else:
            return "application/octet-stream"
    
    def run(self):
        """Run the main application"""
        self.setup_page_config()
        self.load_custom_css()
        self.render_header()
        
        st.markdown("---")
        
        # File upload section
        st.header("📁 Upload Excel Files")
        st.markdown("Upload up to 10 Excel files for batch processing")
        st.info("💡 Supported formats: .xlsx, .xls, .xlsm | Max file size: 50MB each")
        
        uploaded_files = st.file_uploader(
            "Choose Excel files",
            type=['xlsx', 'xls', 'xlsm'],
            accept_multiple_files=True,
            help="Upload Excel files containing Title, Work Order, Bill Quantity, and optionally Extra Items sheets"
        )
        
        if uploaded_files:
            st.success(f"📊 {len(uploaded_files)} file(s) uploaded successfully!")
            
            # Display file information
            with st.expander("📋 File Information"):
                for file in uploaded_files:
                    file_size_mb = file.size / (1024 * 1024)
                    st.write(f"• **{file.name}** ({file_size_mb:.2f} MB)")
                    if file_size_mb > 50:
                        st.error(f"⚠️ File {file.name} exceeds 50MB limit")
            
            # Show processing options
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚀 Process Files", type="primary", key="process_btn"):
                    try:
                        with st.spinner('Processing files...'):
                            self.process_files(uploaded_files)
                    except Exception as e:
                        st.error(f"Error processing files: {str(e)}")
                        st.error(traceback.format_exc())
            
            with col2:
                if st.button("🔄 Clear Files", key="clear_btn"):
                    st.rerun()
        
        # Footer with best wishes
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <p style="color: #4CAF50; font-weight: bold;">
                🌟 Wishing you success in all your professional endeavors! 🌟
            </p>
        </div>
        """, unsafe_allow_html=True)

# Application entry point
if __name__ == "__main__":
    app = BillGeneratorApp()
    app.run()
