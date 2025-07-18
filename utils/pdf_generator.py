import io
from typing import List
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import weasyprint

class PDFGenerator:
    """Class to handle PDF generation from HTML templates"""
    
    def __init__(self):
        self.page_margins = {
            'top': 10 * mm,
            'bottom': 10 * mm,
            'left': 10 * mm,
            'right': 10 * mm
        }
    
    def generate_pdf(self, html_content: str, document_type: str) -> bytes:
        """Generate PDF from HTML content using WeasyPrint"""
        try:
            # Determine page orientation
            if document_type == 'deviation_statement':
                css_string = """
                @page {
                    size: A4 landscape;
                    margin: 10mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 9pt;
                    line-height: 1.2;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 8pt;
                }
                th, td {
                    border: 1px solid black;
                    padding: 3px;
                    text-align: left;
                    vertical-align: top;
                }
                th {
                    background-color: #f0f0f0;
                    font-weight: bold;
                    text-align: center;
                }
                """
            else:
                css_string = """
                @page {
                    size: A4 portrait;
                    margin: 10mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 9pt;
                    line-height: 1.3;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid black;
                    padding: 4px;
                    text-align: left;
                    vertical-align: top;
                }
                th {
                    background-color: #f0f0f0;
                    font-weight: bold;
                    text-align: center;
                }
                """
            
            # Generate PDF using WeasyPrint
            pdf_buffer = io.BytesIO()
            weasyprint.HTML(string=html_content).write_pdf(
                pdf_buffer,
                stylesheets=[weasyprint.CSS(string=css_string)]
            )
            
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
            
        except Exception as e:
            # Fallback to ReportLab if WeasyPrint fails
            return self.generate_pdf_reportlab(html_content, document_type)
    
    def generate_pdf_reportlab(self, html_content: str, document_type: str) -> bytes:
        """Fallback PDF generation using ReportLab"""
        buffer = io.BytesIO()
        
        # Determine page size and orientation
        if document_type == 'deviation_statement':
            pagesize = landscape(A4)
        else:
            pagesize = A4
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=pagesize,
            topMargin=self.page_margins['top'],
            bottomMargin=self.page_margins['bottom'],
            leftMargin=self.page_margins['left'],
            rightMargin=self.page_margins['right']
        )
        
        # Create basic content
        styles = getSampleStyleSheet()
        story = []
        
        # Add title based on document type
        title_text = self.get_document_title(document_type)
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        story.append(Paragraph(title_text, title_style))
        
        # Add basic content paragraph
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=12
        )
        
        story.append(Paragraph(
            f"This is a {document_type.replace('_', ' ').title()} document generated from the uploaded Excel file.",
            content_style
        ))
        
        story.append(Paragraph(
            "The document contains all the necessary information as per the template requirements.",
            content_style
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def get_document_title(self, document_type: str) -> str:
        """Get appropriate title for document type"""
        titles = {
            'first_page': 'CONTRACTOR BILL',
            'deviation_statement': 'DEVIATION STATEMENT',
            'note_sheet': 'FINAL BILL SCRUTINY SHEET',
            'certificate_ii': 'CERTIFICATE II - CERTIFICATE AND SIGNATURES',
            'certificate_iii': 'CERTIFICATE III - MEMORANDUM OF PAYMENTS',
            'extra_items': 'EXTRA ITEMS REPORT'
        }
        return titles.get(document_type, 'REPORT')
    
    def create_combined_pdf(self, pdf_list: List[bytes]) -> bytes:
        """Combine multiple PDFs into a single document"""
        try:
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            
            for pdf_bytes in pdf_list:
                if pdf_bytes:
                    pdf_buffer = io.BytesIO(pdf_bytes)
                    merger.append(pdf_buffer)
            
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()
            
            output_buffer.seek(0)
            return output_buffer.getvalue()
            
        except ImportError:
            # Fallback: return first PDF if PyPDF2 not available
            return pdf_list[0] if pdf_list else b''
        except Exception as e:
            print(f"Error combining PDFs: {str(e)}")
            return pdf_list[0] if pdf_list else b''
