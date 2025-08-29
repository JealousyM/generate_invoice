#!/usr/bin/env python3
"""
Invoice Generator Script

Usage: python generate_invoice.py <date> <end_date> <buyer> <recipient> <amount>
Example: python generate_invoice.py 04.09.2025 14/09/2025 Retano-Latvia Retano-Latvia 3000.00
"""

import sys
import json
import argparse
import requests
from datetime import datetime
from docx import Document
from docx2pdf import convert
import os
from pathlib import Path
from number_converter import NumberToWords

class InvoiceGenerator:
    def __init__(self):
        self.orgs_data = self.load_organizations()
    
    def load_organizations(self):
        """Load organization data from orgs.json"""
        try:
            with open('orgs.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: orgs.json file not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in orgs.json")
            sys.exit(1)
    
    def get_org_data(self, org_name):
        """Get organization data by name"""
        for org in self.orgs_data:
            if org['name'] == org_name:
                return org['data']
        return f"Organization '{org_name}' not found"
    
    def parse_date(self, date_str):
        """Parse date string in DD.MM.YYYY format"""
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'. Expected DD.MM.YYYY")
            sys.exit(1)
    
    def parse_end_date(self, date_str):
        """Parse end date string in DD/MM/YYYY format"""
        try:
            return datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            print(f"Error: Invalid end date format '{date_str}'. Expected DD/MM/YYYY")
            sys.exit(1)
    
    def get_nbp_rate(self, date):
        """Fetch NBP exchange rate for given date"""
        try:
            # NBP API format: YYYY-MM-DD
            date_str = date.strftime('%Y-%m-%d')
            url = f"http://api.nbp.pl/api/exchangerates/rates/a/eur/{date_str}/"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['rates'][0]['mid']
            else:
                print(f"Warning: Could not fetch NBP rate for {date_str}, using default 4.30")
                return 4.30
        except Exception as e:
            print(f"Warning: Error fetching NBP rate: {e}, using default 4.30")
            return 4.30
    
    def amount_to_words_polish(self, amount):
        """Convert amount to words in Polish"""
        return NumberToWords.to_polish(amount)
    
    def amount_to_words_english(self, amount):
        """Convert amount to words in English"""
        return NumberToWords.to_english(amount)
    
    def convert_to_pdf_docx2pdf(self, docx_path, pdf_path):
        """Convert DOCX to PDF using docx2pdf"""
        try:
            print(f"Starting docx2pdf conversion...")
            print(f"Input file: {docx_path}")
            print(f"Output file: {pdf_path}")
            
            # Check if input file exists
            if not os.path.exists(docx_path):
                print(f"Error: Input file does not exist: {docx_path}")
                return False
            
            # Attempt conversion
            convert(docx_path, pdf_path, keep_active=False)
            
            # Check if output file was created
            if os.path.exists(pdf_path):
                print(f"PDF conversion successful!")
                return True
            else:
                print(f"PDF file was not created: {pdf_path}")
                return False
                
        except ImportError as e:
            print(f"docx2pdf import error: {e}")
            print("Install docx2pdf: pip install docx2pdf")
            return False
        except FileNotFoundError as e:
            print(f"File not found error: {e}")
            print("Make sure Microsoft Word or LibreOffice is installed")
            return False
        except PermissionError as e:
            print(f"Permission error: {e}")
            print("Check if the file is open in another application")
            return False
        except Exception as e:
            print(f"Unexpected error in docx2pdf conversion: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
    
    def replace_placeholders(self, doc, replacements):
        """Replace placeholders in Word document while preserving formatting"""
        # Replace in paragraphs
        for paragraph in doc.paragraphs:
            self._replace_in_paragraph(paragraph, replacements)
        
        # Replace in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_in_paragraph(paragraph, replacements)
    
    def _replace_in_paragraph(self, paragraph, replacements):
        """Replace placeholders in a single paragraph while preserving formatting"""
        for placeholder, value in replacements.items():
            if placeholder in paragraph.text:
                # Find all runs that contain parts of the placeholder
                placeholder_start = paragraph.text.find(placeholder)
                if placeholder_start != -1:
                    # Build a list of runs and their positions in the paragraph text
                    runs_info = []
                    text_pos = 0
                    
                    for run in paragraph.runs:
                        run_text = run.text
                        runs_info.append({
                            'run': run,
                            'start': text_pos,
                            'end': text_pos + len(run_text),
                            'text': run_text
                        })
                        text_pos += len(run_text)
                    
                    # Find which runs contain the placeholder
                    placeholder_end = placeholder_start + len(placeholder)
                    affected_runs = []
                    
                    for run_info in runs_info:
                        # Check if this run intersects with the placeholder
                        if (run_info['start'] < placeholder_end and 
                            run_info['end'] > placeholder_start):
                            affected_runs.append(run_info)
                    
                    if affected_runs:
                        # Replace text in affected runs
                        first_run = affected_runs[0]
                        
                        # Calculate positions within the first run
                        rel_start = max(0, placeholder_start - first_run['start'])
                        
                        if len(affected_runs) == 1:
                            # Placeholder is within a single run
                            run = first_run['run']
                            rel_end = rel_start + len(placeholder)
                            new_text = (run.text[:rel_start] + 
                                      str(value) + 
                                      run.text[rel_end:])
                            run.text = new_text
                        else:
                            # Placeholder spans multiple runs
                            # Clear text from all affected runs except the first
                            for i in range(1, len(affected_runs)):
                                affected_runs[i]['run'].text = ""
                            
                            # Replace in the first run
                            first_run['run'].text = (first_run['text'][:rel_start] + str(value))
                            
                            # Handle the last run if placeholder doesn't end exactly at run boundary
                            last_run = affected_runs[-1]
                            chars_from_start = placeholder_end - last_run['start']
                            if chars_from_start < len(last_run['text']):
                                last_run['run'].text = last_run['text'][chars_from_start:]
    
    def generate_invoice(self, date_str, end_date_str, buyer, recipient, amount):
        """Generate invoice document"""
        # Parse dates
        start_date = self.parse_date(date_str)
        end_date = self.parse_end_date(end_date_str)
        
        # Get NBP rate
        nbp_rate = self.get_nbp_rate(start_date)
        
        # Get organization data
        buyer_data = self.get_org_data(buyer)
        recipient_data = self.get_org_data(recipient)
        
        # Convert amount to words
        amount_polish = self.amount_to_words_polish(amount)
        amount_english = self.amount_to_words_english(amount)
        
        # Prepare replacements
        replacements = {
            '<dd>': start_date.strftime('%d'),
            '<mm>': start_date.strftime('%m'),
            '<yyyy>': start_date.strftime('%Y'),
            '<buyer>': buyer_data,
            '<recipient>': recipient_data,
            '<summ>': amount,
            '<termin>': end_date.strftime('%d/%m/%Y'),
            '<summ_words_polland>': amount_polish,
            '<summ_words_english>': amount_english,
            '<nbp_kurs>': str(nbp_rate)
        }
        
        # Load template
        try:
            doc = Document('invoice_template.docx')
        except FileNotFoundError:
            print("Error: invoice_template.docx not found")
            sys.exit(1)
        
        # Replace placeholders
        self.replace_placeholders(doc, replacements)
        
        # Create invoices directory if it doesn't exist
        invoices_dir = "invoices"
        os.makedirs(invoices_dir, exist_ok=True)
        
        # Generate output filename
        filename = f"Peraviortkin_Mi_code_{date_str}.docx"
        output_filename = os.path.join(invoices_dir, filename)
        
        # Save DOCX (without opening)
        try:
            # Save document with specific settings to prevent auto-opening
            doc.save(output_filename)
            print(f"Generated DOCX: {output_filename}")
        except Exception as e:
            print(f"Error saving DOCX: {e}")
            return
        
  

def main():
    if len(sys.argv) != 6:
        print("Usage: python generate_invoice.py <date> <end_date> <buyer> <recipient> <amount>")
        print("Example: python generate_invoice.py 04.09.2025 14/09/2025 Retano-Latvia Retano-Latvia 3000.00")
        sys.exit(1)
    
    date_str = sys.argv[1]
    end_date_str = sys.argv[2]
    buyer = sys.argv[3]
    recipient = sys.argv[4]
    amount = sys.argv[5]
    
    generator = InvoiceGenerator()
    generator.generate_invoice(date_str, end_date_str, buyer, recipient, amount)

if __name__ == "__main__":
    main()
