from typing import Dict, Any
import math
from .template_renderer import TemplateRenderer

class ReportGenerator:
    """Class to generate all types of reports from processed data"""
    
    def __init__(self):
        self.template_renderer = TemplateRenderer()
        self.tender_premium_percent = 0.04  # 4% default
    
    def generate_all_reports(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate all report types from processed data"""
        # Calculate totals and prepare data
        report_data = self.prepare_report_data(data)
        
        reports = {
            'first_page_html': self.generate_first_page_report(report_data),
            'deviation_statement_html': self.generate_deviation_statement(report_data),
            'note_sheet_html': self.generate_note_sheet(report_data),
            'certificate_ii_html': self.generate_certificate_ii(report_data),
            'certificate_iii_html': self.generate_certificate_iii(report_data)
        }
        
        # Add extra items report if data exists
        if report_data.get('extra_items'):
            reports['extra_items_html'] = self.generate_extra_items_report(report_data)
        
        return reports
    
    def prepare_report_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and calculate all necessary data for reports"""
        # Extract basic info
        title_data = data.get('title_data', {})
        work_order_data = data.get('work_order_data', {})
        bill_quantity_data = data.get('bill_quantity_data', {})
        extra_items_data = data.get('extra_items_data', {})
        
        # Merge work order and bill quantity data
        merged_items = self.merge_work_order_and_bill_data(
            work_order_data.get('items', []),
            bill_quantity_data.get('items', [])
        )
        
        # Calculate main bill totals
        bill_total = sum(item.get('amount_bill', 0) for item in merged_items)
        bill_premium = bill_total * self.tender_premium_percent
        bill_grand_total = bill_total + bill_premium
        
        # Calculate extra items totals
        extra_items = extra_items_data.get('items', []) if extra_items_data else []
        extra_items_base = sum(item.get('amount', 0) for item in extra_items)
        extra_premium = extra_items_base * self.tender_premium_percent
        extra_items_sum = extra_items_base + extra_premium
        
        # Calculate final totals
        grand_total = bill_grand_total + extra_items_sum
        
        # Calculate deductions
        sd_amount = grand_total * 0.10  # 10% Security Deposit
        it_amount = grand_total * 0.02  # 2% Income Tax
        gst_amount = self.round_up_to_even(grand_total * 0.02)  # 2% GST rounded up to even
        lc_amount = grand_total * 0.01  # 1% Labour Cess
        
        total_deductions = sd_amount + it_amount + gst_amount + lc_amount
        net_payable = grand_total - total_deductions
        
        # Prepare comprehensive data structure
        report_data = {
            # Basic information
            'agreement_no': title_data.get('agreement_no', ''),
            'name_of_work': title_data.get('name_of_work', ''),
            'name_of_firm': title_data.get('name_of_firm', ''),
            'date_commencement': title_data.get('date_commencement', ''),
            'date_completion': title_data.get('date_completion', ''),
            'actual_completion': title_data.get('actual_completion', title_data.get('date_completion', '')),
            'measurement_date': title_data.get('measurement_date', ''),
            
            # Items data
            'bill_items': merged_items,
            'extra_items': extra_items,
            'deviation_items': self.prepare_deviation_items(merged_items),
            
            # Financial calculations
            'work_order_amount': work_order_data.get('total', 0),
            'bill_total': bill_total,
            'bill_premium': bill_premium,
            'bill_grand_total': bill_grand_total,
            'extra_items_base': extra_items_base,
            'extra_premium': extra_premium,
            'extra_items_sum': extra_items_sum,
            'tender_premium_percent': self.tender_premium_percent,
            
            # Summary totals
            'totals': {
                'grand_total': grand_total,
                'sd_amount': sd_amount,
                'it_amount': it_amount,
                'gst_amount': gst_amount,
                'lc_amount': lc_amount,
                'total_deductions': total_deductions,
                'net_payable': net_payable
            },
            
            # Additional data for certificates
            'measurement_officer': 'JEN AC',
            'measurement_book_no': '887',
            'measurement_book_page': '04-20',
            'officer_name': 'Premlata Jain',
            'officer_designation': 'AAO - As Auditor',
            'authorising_officer_name': 'Executive Engineer',
            'authorising_officer_designation': 'PWD Udaipur',
            'payable_words': self.number_to_words(net_payable),
            
            # Last bill amount (zero for first bill)
            'last_bill_amount': 0.00,  # Default to 0 for first bill
            
            # Notes for note sheet
            'notes': self.generate_notes(grand_total, work_order_data.get('total', 0), extra_items_sum)
        }
        
        return report_data
    
    def merge_work_order_and_bill_data(self, work_order_items, bill_items):
        """Merge work order and bill quantity data"""
        merged = []
        
        # Create lookup for bill items by serial number
        bill_lookup = {item.get('serial_no', ''): item for item in bill_items}
        
        for wo_item in work_order_items:
            serial_no = wo_item.get('serial_no', '')
            bill_item = bill_lookup.get(serial_no, {})
            
            merged_item = {
                'serial_no': serial_no,
                'description': wo_item.get('description', ''),
                'unit': wo_item.get('unit', ''),
                'quantity_wo': wo_item.get('quantity', 0),
                'rate': wo_item.get('rate', 0),
                'amount_wo': wo_item.get('amount', 0),
                'quantity_bill': bill_item.get('quantity_bill', 0),
                'amount_bill': bill_item.get('amount_bill', 0),
                'remark': wo_item.get('remark', '')
            }
            
            merged.append(merged_item)
        
        return merged
    
    def prepare_deviation_items(self, merged_items):
        """Prepare deviation analysis for each item"""
        deviation_items = []
        
        for item in merged_items:
            qty_wo = item.get('quantity_wo', 0)
            qty_bill = item.get('quantity_bill', 0)
            rate = item.get('rate', 0)
            
            # Calculate excess and saving
            if qty_bill > qty_wo:
                excess_qty = qty_bill - qty_wo
                excess_amt = excess_qty * rate
                saving_qty = 0
                saving_amt = 0
            else:
                excess_qty = 0
                excess_amt = 0
                saving_qty = qty_wo - qty_bill
                saving_amt = saving_qty * rate
            
            deviation_item = {
                'serial_no': item.get('serial_no', ''),
                'description': item.get('description', ''),
                'unit': item.get('unit', ''),
                'qty_wo': qty_wo,
                'rate': rate,
                'amt_wo': item.get('amount_wo', 0),
                'qty_bill': qty_bill,
                'amt_bill': item.get('amount_bill', 0),
                'excess_qty': excess_qty,
                'excess_amt': excess_amt,
                'saving_qty': saving_qty,
                'saving_amt': saving_amt,
                'remark': item.get('remark', '')
            }
            
            deviation_items.append(deviation_item)
        
        return deviation_items
    
    def generate_first_page_report(self, data):
        """Generate first page report HTML"""
        return self.template_renderer.render_template('first_page.html', data)
    
    def generate_deviation_statement(self, data):
        """Generate deviation statement HTML"""
        # Calculate deviation summary
        deviation_summary = self.calculate_deviation_summary(data)
        data['deviation_summary'] = deviation_summary
        
        # Add extra items to deviation if they exist
        if data.get('extra_items'):
            data['extra_items_for_deviation'] = self.prepare_extra_items_for_deviation(data.get('extra_items', []))
        
        return self.template_renderer.render_template('deviation_statement.html', data)
    
    def generate_note_sheet(self, data):
        """Generate note sheet HTML"""
        return self.template_renderer.render_template('note_sheet.html', data)
    
    def generate_certificate_ii(self, data):
        """Generate Certificate II HTML"""
        return self.template_renderer.render_template('certificate_ii.html', data)
    
    def generate_certificate_iii(self, data):
        """Generate Certificate III HTML"""
        return self.template_renderer.render_template('certificate_iii.html', data)
    
    def generate_extra_items_report(self, data):
        """Generate extra items report HTML"""
        return self.template_renderer.render_template('extra_items.html', data)
    
    def calculate_deviation_summary(self, data):
        """Calculate deviation summary totals"""
        deviation_items = data.get('deviation_items', [])
        extra_items = data.get('extra_items', [])
        
        # Calculate totals from regular deviation items
        work_order_total = sum(item.get('amt_wo', 0) for item in deviation_items)
        executed_total = sum(item.get('amt_bill', 0) for item in deviation_items)
        overall_excess = sum(item.get('excess_amt', 0) for item in deviation_items)
        overall_saving = sum(item.get('saving_amt', 0) for item in deviation_items)
        
        # Add extra items to totals (all extra items are considered excess)
        extra_items_total = sum(item.get('amount', 0) for item in extra_items)
        executed_total += extra_items_total
        overall_excess += extra_items_total
        
        tender_premium_percent = data.get('tender_premium_percent', 0.04)
        
        # Calculate with tender premium
        tender_premium_f = work_order_total * tender_premium_percent
        grand_total_f = work_order_total + tender_premium_f
        
        tender_premium_h = executed_total * tender_premium_percent
        grand_total_h = executed_total + tender_premium_h
        
        tender_premium_j = overall_excess * tender_premium_percent
        grand_total_j = overall_excess + tender_premium_j
        
        tender_premium_l = overall_saving * tender_premium_percent
        grand_total_l = overall_saving + tender_premium_l
        
        net_difference = grand_total_h - grand_total_f
        
        return {
            'work_order_total': work_order_total,
            'executed_total': executed_total,
            'overall_excess': overall_excess,
            'overall_saving': overall_saving,
            'tender_premium_f': tender_premium_f,
            'grand_total_f': grand_total_f,
            'tender_premium_h': tender_premium_h,
            'grand_total_h': grand_total_h,
            'tender_premium_j': tender_premium_j,
            'grand_total_j': grand_total_j,
            'tender_premium_l': tender_premium_l,
            'grand_total_l': grand_total_l,
            'net_difference': net_difference
        }
    
    def round_up_to_even(self, value):
        """Round up to the next even number"""
        rounded = math.ceil(value)
        return rounded if rounded % 2 == 0 else rounded + 1
    
    def number_to_words(self, number):
        """Convert number to words (simplified implementation)"""
        # This is a simplified implementation
        # In production, you might want to use a library like num2words
        try:
            return f"Rupees {int(number):,} only"
        except:
            return "Amount in words"
    
    def generate_notes(self, grand_total, work_order_amount, extra_items_sum):
        """Generate notes for the note sheet"""
        percentage_completion = (grand_total / work_order_amount * 100) if work_order_amount > 0 else 0
        extra_percentage = (extra_items_sum / work_order_amount * 100) if work_order_amount > 0 else 0
        
        notes = [
            f"The work has been completed {percentage_completion:.2f}% of the Work Order Amount.",
            "Requisite Deviation Statement is enclosed. The Overall Excess is less than or equal to 5% and is having approval jurisdiction under this office.",
            "Work was completed in time.",
            f"The amount of Extra items is Rs. {int(extra_items_sum)} which is {extra_percentage:.2f}% of the Work Order Amount; under 5%, approval of the same is to be granted by this office.",
            "Quality Control (QC) test reports attached.",
            "Please peruse above details for necessary decision-making."
        ]
        
        return notes
    
    def prepare_extra_items_for_deviation(self, extra_items):
        """Prepare extra items for deviation statement"""
        deviation_extra_items = []
        
        for item in extra_items:
            deviation_item = {
                'serial_no': item.get('serial_no', ''),
                'description': item.get('description', ''),
                'unit': item.get('unit', ''),
                'qty_wo': 0,  # Extra items don't have work order quantities
                'rate': item.get('rate', 0),
                'amt_wo': 0,  # Extra items don't have work order amounts
                'qty_bill': item.get('quantity', 0),
                'amt_bill': item.get('amount', 0),
                'excess_qty': item.get('quantity', 0),  # All quantity is excess for extra items
                'excess_amt': item.get('amount', 0),    # All amount is excess for extra items
                'saving_qty': 0,
                'saving_amt': 0,
                'remark': item.get('remark', 'Extra Item')
            }
            deviation_extra_items.append(deviation_item)
        
        return deviation_extra_items
