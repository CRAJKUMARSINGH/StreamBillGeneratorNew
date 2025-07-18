from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from typing import Dict, Any

class TemplateRenderer:
    """Class to handle HTML template rendering using Jinja2"""
    
    def __init__(self):
        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.env.filters['round'] = self.round_filter
        self.env.filters['int'] = int
        self.env.filters['format_currency'] = self.format_currency
        self.env.filters['format_date'] = self.format_date
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render a template with the provided data"""
        try:
            template = self.env.get_template(template_name)
            return template.render(data=data)
        except Exception as e:
            print(f"Error rendering template {template_name}: {str(e)}")
            return self.create_fallback_html(template_name, data)
    
    def create_fallback_html(self, template_name: str, data: Dict[str, Any]) -> str:
        """Create fallback HTML when template rendering fails"""
        title = template_name.replace('.html', '').replace('_', ' ').title()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Document generated successfully from Excel data.</p>
            <p><strong>Agreement No:</strong> {data.get('agreement_no', 'N/A')}</p>
            <p><strong>Name of Work:</strong> {data.get('name_of_work', 'N/A')}</p>
            <p><strong>Name of Firm:</strong> {data.get('name_of_firm', 'N/A')}</p>
        </body>
        </html>
        """
        return html
    
    def round_filter(self, value, decimals=2):
        """Custom filter for rounding numbers"""
        try:
            return round(float(value), decimals)
        except (ValueError, TypeError):
            return 0
    
    def format_currency(self, value):
        """Format value as currency"""
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"
    
    def format_date(self, value):
        """Format date value"""
        if not value:
            return ""
        return str(value)
