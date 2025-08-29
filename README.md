# Invoice Generator with Telegram Bot

🚨 **IMPORTANT: Python 3.13 Compatible Version**

Automated invoice generation system with Telegram bot support, adapted for **Python 3.13** and **python-telegram-bot 21.8**.

## Features

### ✅ Working Features
- 📄 DOCX invoice generation from Word template
- 🔄 Automatic placeholder replacement with data
- 💱 NBP (National Bank of Poland) exchange rate fetching
- 🔤 Amount conversion to words (Polish and English)
- 📂 Save to `invoices/` folder
- 🏢 Multiple organizations support
- 🤖 **Telegram Bot (version 21.8) - FULLY WORKING**
- 🔒 User access control

### ⚠️ Disabled Features
- ❌ PDF generation (compatibility issues with Python 3.13)

## System Requirements

- **Python 3.13** (required!)
- pip package manager
- Internet connection for NBP rate fetching

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Telegram Bot Setup (recommended)

#### Create Bot via BotFather
1. Find @BotFather in Telegram
2. Send `/newbot`
3. Follow the instructions
4. Save the token

#### Automatic Setup
```bash
python setup.py
# OR directly:
python bot/setup_bot.py
```

#### Run the Bot
```bash
python start_bot.py
# OR directly:
python bot/telegram_bot.py
```

## Available Files

### Root Directory
- ✅ **`start_bot.py`** - Convenience bot launcher
- ✅ **`setup.py`** - Convenience setup launcher  
- ✅ `generate_invoice.py` - CLI invoice generator (without PDF)
- 📋 `requirements.txt` - Dependencies
- 📝 `config.env` - Configuration (created during setup)

### Bot Directory (`bot/`)
- 🤖 `telegram_bot.py` - Main Telegram bot
- ⚙️ `setup_bot.py` - Bot configuration setup
- 🧪 `test_generate.py` - Test bot version
- 🔄 `run_bot.py` - Auto-restart bot runner

### Converter Directory (`converter/`)
- 🔤 `number_converter.py` - Number to words converter

### Resources Directory (`resources/`)
- 📄 `invoice_template.docx` - Invoice template
- 📊 `orgs.json` - Organization data

## Telegram Bot Commands

### `/start`
Welcome message and basic information

### `/generate`
Create invoice
```
/generate <date> <end_date> <buyer> <recipient> <amount>
```

**Example:**
```
/generate 04.09.2025 14/09/2025 Organization Organization 3000.00
```

### `/status`
Check system status

### `/orgs`
List available organizations

### `/help`
Command help

## Data Formats

- **Date:** DD.MM.YYYY (04.09.2025)
- **End Date:** DD/MM/YYYY (14/09/2025)
- **Amount:** Number with dot (3000.00)

## CLI Usage

```bash
python generate_invoice.py 04.09.2025 "14/09/2025" "Organization" "Organization" 3000.00
```

## Project Structure

```
generate-invoice/
├── 📂 bot/                       # Telegram bot files
│   ├── 🤖 telegram_bot.py        # Main Telegram bot
│   ├── ⚙️ setup_bot.py          # Bot configuration setup
│   ├── 🧪 test_generate.py      # Test bot version
│   └── 🔄 run_bot.py            # Auto-restart bot runner
├── 📂 converter/                 # Conversion utilities
│   └── 🔤 number_converter.py   # Number to words converter
├── 📂 resources/                 # Templates and data
│   ├── 📄 invoice_template.docx  # Invoice template
│   └── 📊 orgs.json             # Organization data
├── 📂 invoices/                  # Generated invoices (created automatically)
├── 🚀 start_bot.py              # Convenience bot launcher
├── ⚙️ setup.py                  # Convenience setup launcher
├── 🔧 generate_invoice.py       # CLI invoice generator
├── 📋 requirements.txt           # Dependencies
└── 📝 config.env                # Configuration (created during setup)
```

## Template Placeholders

In the `resources/invoice_template.docx` file, these placeholders are replaced:

- `<dd>` - Day
- `<mm>` - Month  
- `<yyyy>` - Year
- `<buyer>` - Buyer data
- `<recipient>` - Recipient data
- `<summ>` - Amount
- `<termin>` - Payment deadline
- `<summ_words_polland>` - Amount in words (Polish)
- `<summ_words_english>` - Amount in words (English)
- `<nbp_kurs>` - NBP EUR exchange rate

## Organization Configuration

File `resources/orgs.json`:
```json
[
    {
        "name": "Organization",
        "data": "RETANO SOLUTIONS LTD\nVesetas 7, Riga, LATVIA\nBank: АО Rietumu Banka\nNr rachunku/ Bank account number: LV72RTMB0000700806618\nSWIFT: RTMBLV2X"
    }
]
```

## Fixed Issues

### ✅ Python 3.13 Compatibility
- Used compatible version python-telegram-bot 21.8
- Fixed all issues with `imghdr` module
- Updated imports for new API

### ✅ Telegram Bot Issues  
- Fixed "Application object has no attribute" error
- Correct async/await operation
- Proper Markdown V2 formatting
- Stable polling operation

### ✅ Stability
- Removed problematic PDF generation
- Improved error handling
- Detailed logging

## Dependencies

```txt
python-docx==1.1.2
docx2pdf==0.1.8
requests==2.31.0
python-telegram-bot==21.8
python-dotenv==1.0.0
```

## Troubleshooting

### Version Check
```bash
python --version          # Should be 3.13.x
pip show python-telegram-bot  # Should be 21.8
```

### Reinstallation
```bash
pip install python-telegram-bot==21.8 --force-reinstall
pip install -r requirements.txt --force-reinstall
```

### Bot Issues
1. **Use `python start_bot.py` or `python bot/telegram_bot.py`**
2. Check token in `config.env`
3. Make sure User ID is in ALLOWED_USER_IDS
4. Check internet connection

### PDF Generation
⚠️ **PDF generation disabled** due to compatibility issues.
Use DOCX files or convert manually.

## Example Session

```bash
# 1. Installation
pip install -r requirements.txt

# 2. Bot setup
python setup.py

# 3. Start bot
python start_bot.py

# 4. In Telegram:
/start
/generate 04.09.2025 14/09/2025 Organization Organization 3000.00
```

## Security

- 🔒 Never publish `config.env`
- 👥 Restrict access via ALLOWED_USER_IDS
- 🔑 Regularly change bot token

## Technical Notes

- ⚡ Fully compatible with Python 3.13
- 🤖 Uses python-telegram-bot 21.8 (latest stable)
- 🔄 All async functions correctly implemented
- 📝 Markdown V2 formatting
- 🛡️ Robust error handling

---

## Status: ✅ FULLY WORKING

Project fully working with Python 3.13 and Telegram Bot API 21.8!

## License

MIT License