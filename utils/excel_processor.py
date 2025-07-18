import pandas as pd
import io
from typing import Dict, Any, Optional
import traceback

class ExcelProcessor:
    """Class to handle Excel file processing and data extraction"""
    
    def __init__(self):
        self.required_sheets = ['Title', 'Work Order', 'Bill Quantity']
        self.optional_sheets = ['Extra Items']
    
    def process_excel_file(self, uploaded_file) -> Optional[Dict[str, Any]]:
        """Process an uploaded Excel file and extract data from all sheets"""
        try:
            # Validate file before processing
            if not uploaded_file:
                raise ValueError("No file provided")
                
            if uploaded_file.size == 0:
                raise ValueError("Empty file provided")
                
            # Read file content into bytes first
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            # Read all sheets using BytesIO
            excel_data = pd.read_excel(io.BytesIO(file_content), sheet_name=None, engine='openpyxl')
            
            # Validate required sheets
            available_sheets = list(excel_data.keys())
            missing_sheets = [sheet for sheet in self.required_sheets if sheet not in available_sheets]
            if missing_sheets:
                raise ValueError(f"Missing required sheets: {missing_sheets}. Available sheets: {available_sheets}")
            
            # Extract data from each sheet
            processed_data = {
                'filename': uploaded_file.name,
                'title_data': self.process_title_sheet(excel_data.get('Title')),
                'work_order_data': self.process_work_order_sheet(excel_data.get('Work Order')),
                'bill_quantity_data': self.process_bill_quantity_sheet(excel_data.get('Bill Quantity')),
                'extra_items_data': self.process_extra_items_sheet(excel_data.get('Extra Items')) if 'Extra Items' in excel_data else None
            }
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing Excel file {uploaded_file.name if uploaded_file else 'Unknown'}: {str(e)}")
            print(traceback.format_exc())
            return None
    
    def process_title_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract title and header information"""
        if df is None:
            return {}
        
        # Convert DataFrame to dictionary for easier processing
        title_info = {}
        
        # Extract key information from title sheet
        for idx, row in df.iterrows():
            if pd.notna(row.iloc[0]):
                key = str(row.iloc[0]).strip()
                value = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                
                # Map common fields
                if 'agreement' in key.lower():
                    title_info['agreement_no'] = value
                elif 'work' in key.lower() and 'name' in key.lower():
                    title_info['name_of_work'] = value
                elif 'firm' in key.lower() or 'contractor' in key.lower():
                    title_info['name_of_firm'] = value
                elif 'commencement' in key.lower():
                    title_info['date_commencement'] = self.format_date(value)
                elif 'completion' in key.lower():
                    title_info['date_completion'] = self.format_date(value)
                elif 'measurement' in key.lower():
                    title_info['measurement_date'] = self.format_date(value)
        
        return title_info
    
    def process_work_order_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process work order data"""
        if df is None:
            return {'items': [], 'total': 0}
        
        items = []
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Process each row
        for idx, row in df.iterrows():
            # Skip header rows and empty rows
            if pd.isna(row.iloc[0]) or 'serial' in str(row.iloc[0]).lower():
                continue
            
            # Only include serial number if it exists and is not empty/blank
            serial_val = row.iloc[0] if pd.notna(row.iloc[0]) else ''
            serial_no = str(serial_val).strip() if serial_val and str(serial_val).strip() and str(serial_val).strip() != 'nan' else ''
            
            item = {
                'serial_no': serial_no,
                'description': str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else '',
                'unit': str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else '',
                'quantity': self.safe_float(row.iloc[3]) if len(row) > 3 else 0,
                'rate': self.safe_float(row.iloc[4]) if len(row) > 4 else 0,
                'amount': self.safe_float(row.iloc[5]) if len(row) > 5 else 0,
                'remark': str(row.iloc[6]).strip() if len(row) > 6 and pd.notna(row.iloc[6]) else ''
            }
            
            # Calculate amount if not provided
            if item['amount'] == 0 and item['quantity'] > 0 and item['rate'] > 0:
                item['amount'] = item['quantity'] * item['rate']
            
            items.append(item)
        
        # Calculate total
        total = sum(item['amount'] for item in items)
        
        return {'items': items, 'total': total}
    
    def process_bill_quantity_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process bill quantity data"""
        if df is None:
            return {'items': [], 'total': 0}
        
        items = []
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Process each row
        for idx, row in df.iterrows():
            # Skip header rows and empty rows
            if pd.isna(row.iloc[0]) or 'serial' in str(row.iloc[0]).lower():
                continue
            
            # Only process rows with non-zero quantities
            quantity = self.safe_float(row.iloc[3]) if len(row) > 3 else 0
            if quantity <= 0:
                continue
            
            # Only include serial number if it exists and is not empty/blank
            serial_val = row.iloc[0] if pd.notna(row.iloc[0]) else ''
            serial_no = str(serial_val).strip() if serial_val and str(serial_val).strip() and str(serial_val).strip() != 'nan' else ''
            
            item = {
                'serial_no': serial_no,
                'description': str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else '',
                'unit': str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else '',
                'quantity_bill': quantity,
                'rate': self.safe_float(row.iloc[4]) if len(row) > 4 else 0,
                'amount_bill': self.safe_float(row.iloc[5]) if len(row) > 5 else 0,
                'remark': str(row.iloc[6]).strip() if len(row) > 6 and pd.notna(row.iloc[6]) else ''
            }
            
            # Calculate amount if not provided
            if item['amount_bill'] == 0 and item['quantity_bill'] > 0 and item['rate'] > 0:
                item['amount_bill'] = item['quantity_bill'] * item['rate']
            
            items.append(item)
        
        # Calculate total
        total = sum(item['amount_bill'] for item in items)
        
        return {'items': items, 'total': total}
    
    def process_extra_items_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process extra items data"""
        if df is None:
            return {'items': [], 'total': 0}
        
        items = []
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Process each row
        for idx, row in df.iterrows():
            # Skip header rows and empty rows
            if pd.isna(row.iloc[0]) or 'serial' in str(row.iloc[0]).lower():
                continue
            
            # Only process rows with non-zero quantities
            quantity = self.safe_float(row.iloc[3]) if len(row) > 3 else 0
            if quantity <= 0:
                continue
            
            # Only include serial number if it exists and is not empty/blank
            serial_val = row.iloc[0] if pd.notna(row.iloc[0]) else ''
            serial_no = str(serial_val).strip() if serial_val and str(serial_val).strip() and str(serial_val).strip() != 'nan' else ''
            
            item = {
                'serial_no': serial_no,
                'description': str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else '',
                'unit': str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else '',
                'quantity': quantity,
                'rate': self.safe_float(row.iloc[4]) if len(row) > 4 else 0,
                'amount': self.safe_float(row.iloc[5]) if len(row) > 5 else 0,
                'remark': str(row.iloc[6]).strip() if len(row) > 6 and pd.notna(row.iloc[6]) else ''
            }
            
            # Calculate amount if not provided
            if item['amount'] == 0 and item['quantity'] > 0 and item['rate'] > 0:
                item['amount'] = item['quantity'] * item['rate']
            
            items.append(item)
        
        # Calculate total
        total = sum(item['amount'] for item in items)
        
        return {'items': items, 'total': total}
    
    def safe_float(self, value) -> float:
        """Safely convert value to float"""
        if pd.isna(value):
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def format_date(self, date_value: str) -> str:
        """Format date to dd/mm/yyyy format"""
        if not date_value or pd.isna(date_value):
            return ""
        
        date_str = str(date_value).strip()
        
        # If already in correct format, return as is
        if '/' in date_str and len(date_str.split('/')) == 3:
            parts = date_str.split('/')
            if len(parts[0]) == 2 and len(parts[1]) == 2 and len(parts[2]) == 4:
                return date_str
        
        # Try to parse and reformat
        try:
            from datetime import datetime
            # Try common formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%d/%m/%Y')
                except ValueError:
                    continue
        except:
            pass
        
        return date_str
