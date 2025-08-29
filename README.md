# Invoice Generator

Python script for generating invoices from a Word template with automatic data replacement and PDF conversion.

## Features

- Replaces placeholders in DOCX template with actual data
- Fetches real-time NBP (National Bank of Poland) exchange rates
- Converts amounts to words in Polish and English
- Generates both DOCX and PDF outputs
- Supports organization data from JSON configuration

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python generate_invoice.py <date> <end_date> <buyer> <recipient> <amount>
```

### Example
```bash
python generate_invoice.py 04.09.2025 14/09/2025 org org 3000.00
```

### Parameters
- `date`: Invoice date in DD.MM.YYYY format (e.g., 04.09.2025)
- `end_date`: Payment deadline in DD/MM/YYYY format (e.g., 14/09/2025)
- `buyer`: Organization name (must exist in orgs.json)
- `recipient`: Organization name (must exist in orgs.json)
- `amount`: Invoice amount in decimal format (e.g., 3000.00)

## Template Placeholders

The script replaces the following placeholders in `invoice_template.docx`:

- `<dd>` - Day from the invoice date
- `<mm>` - Month from the invoice date
- `<yyyy>` - Year from the invoice date
- `<buyer>` - Buyer organization data from orgs.json
- `<recipient>` - Recipient organization data from orgs.json
- `<summ>` - Invoice amount
- `<termin>` - Payment deadline
- `<summ_words_polland>` - Amount in words (Polish)
- `<summ_words_english>` - Amount in words (English)
- `<nbp_kurs>` - NBP EUR exchange rate for the invoice date

## Output

The script generates files in the `invoices/` directory:
- `invoices/Peraviortkin_Mi_code_<date>.docx` - Word document

**Key Features:**
- ✅ Preserves original font formatting when replacing placeholders
- ✅ Creates `invoices/` directory automatically
- ✅ Prevents automatic file opening after generation

## Organization Configuration

Edit `orgs.json` to add/modify organization data:

```json
[
    {
        "name": "org",
        "data": "data"
    }
]
```

## Testing

Run the test script to verify functionality:
```bash
python test_invoice.py
```

## Troubleshooting

### PDF Generation Issues
If PDF generation fails:
1. Install LibreOffice
2. Ensure LibreOffice is in your system PATH
3. On Windows, you may need to restart your terminal after installing LibreOffice

### NBP Rate Fetch Issues
If NBP rate fetching fails, the script will use a default rate of 4.30 EUR/PLN.

### Template Not Found
Ensure `invoice_template.docx` exists in the same directory as the script.

## Requirements

- Python 3.7+
- python-docx
- requests
