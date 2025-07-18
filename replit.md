# Overview

This is a Professional Bill Generator application built with Streamlit that processes Excel files containing construction/contractor billing data and generates multiple standardized PDF reports. The application is designed for clerical-level end users who need to generate professional billing documents from Excel data inputs.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application
- **UI Components**: File upload widgets, progress indicators, download buttons
- **Theme**: Custom balloon animation with best wishes message theme
- **Layout**: Wide layout with sidebar for controls and main content area for results
- **Styling**: Custom CSS with gradient headers and floating balloon animations

## Backend Architecture
- **Language**: Python
- **Architecture Pattern**: Object-oriented with utility classes
- **File Processing**: Pandas for Excel data manipulation
- **Template Engine**: Jinja2 for HTML template rendering
- **PDF Generation**: WeasyPrint for HTML-to-PDF conversion

# Key Components

## Core Application Classes

### BillGeneratorApp (app.py)
- Main application controller
- Handles Streamlit page configuration
- Orchestrates file processing and report generation
- Manages UI layout and user interactions

### ExcelProcessor (utils/excel_processor.py)
- Processes uploaded Excel files with multiple sheets
- Extracts data from required sheets: Title, Work Order, Bill Quantity
- Handles optional Extra Items sheet
- Validates sheet structure and data integrity

### ReportGenerator (utils/report_generator.py)
- Generates multiple report types from processed data
- Calculates totals, premiums, and financial summaries
- Merges work order and bill quantity data
- Handles deviation calculations and extra items processing

### TemplateRenderer (utils/template_renderer.py)
- Renders HTML templates using Jinja2 engine
- Provides custom filters for currency, date, and number formatting
- Creates fallback HTML when template rendering fails
- Manages template loading from templates directory

### PDFGenerator (utils/pdf_generator.py)
- Converts HTML content to PDF using WeasyPrint
- Handles different page orientations (portrait/landscape)
- Applies document-specific styling and formatting
- Manages page margins and layout constraints

## Template System
- **Location**: templates/ directory
- **Format**: HTML with Jinja2 templating
- **Documents**: 
  - first_page.html - Main contractor bill
  - deviation_statement.html - Deviation analysis (landscape)
  - note_sheet.html - Final bill scrutiny sheet
  - certificate_ii.html - Certificate II document
  - certificate_iii.html - Certificate III memorandum
  - extra_items.html - Extra items listing

## Asset Management
- **CSS Styling**: assets/style.css with gradient themes and animations
- **JavaScript**: assets/balloon.js for floating balloon animations
- **Theme Elements**: Logo integration, balloon animations, best wishes messaging

# Data Flow

1. **File Upload**: Users upload up to 10 Excel files simultaneously
2. **Excel Processing**: Each file is validated and data extracted from required sheets
3. **Data Validation**: Checks for required sheets (Title, Work Order, Bill Quantity)
4. **Data Preparation**: Merges work order and bill data, calculates totals and premiums
5. **Report Generation**: Creates multiple HTML reports using Jinja2 templates
6. **PDF Conversion**: Converts HTML to PDF with document-specific formatting
7. **Batch Processing**: Creates ZIP archive with all generated PDFs
8. **Download Delivery**: Provides download links for individual PDFs and batch ZIP

## Key Data Structures
- **Title Data**: Agreement details, dates, firm information
- **Work Order Data**: Original quantities, rates, and amounts
- **Bill Quantity Data**: Executed quantities and calculations
- **Extra Items Data**: Additional work items and costs
- **Merged Data**: Combined work order and bill data with calculations

# External Dependencies

## Core Libraries
- **streamlit**: Web application framework
- **pandas**: Excel file processing and data manipulation
- **openpyxl**: Excel file reading engine
- **jinja2**: HTML template rendering
- **weasyprint**: HTML to PDF conversion

## Supporting Libraries
- **io**: File stream handling
- **zipfile**: Archive creation for batch downloads
- **base64**: File encoding for downloads
- **datetime**: Date formatting and processing
- **pathlib**: File path management

## Template Dependencies
- **HTML/CSS**: Standard web technologies for document layout
- **Jinja2 Filters**: Custom filters for number, currency, and date formatting

# Deployment Strategy

## Application Structure
- **Entry Point**: app.py - main Streamlit application
- **Utilities**: utils/ directory with specialized processing classes
- **Templates**: templates/ directory with HTML document templates
- **Assets**: assets/ directory with CSS and JavaScript for theming

## File Processing Capabilities
- **Batch Processing**: Handles up to 10 Excel files simultaneously
- **Error Handling**: Graceful failure handling with detailed error messages
- **Memory Management**: Stream-based processing for large files
- **Output Management**: Individual and batch download options

## Theme Preservation Requirements
- **Logo Integration**: Maintains selected logo in application header
- **Balloon Animation**: Preserves floating balloon animation effects
- **Best Wishes Theme**: Maintains celebratory messaging theme
- **Custom Styling**: Gradient backgrounds and professional appearance

## Production Considerations
- **Error Recovery**: Robust error handling without application crashes
- **Performance**: Optimized for processing multiple large Excel files
- **User Experience**: Clear progress indicators and status messages
- **Document Quality**: Professional-grade PDF output matching sample formats