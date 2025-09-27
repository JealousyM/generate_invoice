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
- 📬 Gmail listener forwards new emails from configured correspondents to the bot
- 🤖 **Telegram Bot (version 21.8) - FULLY WORKING**
- 🔒 User access control
- 📊 **Jira Work Reports - NEW FEATURE**

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

### 3. Gmail Listener Setup (optional)

1. Enable [IMAP access](https://support.google.com/mail/answer/7126229) for the Gmail account.
2. Create an [app password](https://support.google.com/mail/answer/185833) (required when 2FA is enabled).
3. Open `config.env` and set:
   - `ALLOWED_USER_IDS`
   - `GMAIL_USERNAME`, `GMAIL_APP_PASSWORD`, `CORRESPONDENTS`, `MAIL_CHECK_INTERVAL`
4. Restart the bot so the new configuration loads.

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

### `/report`
Generate Jira work report for a specific month
```
/report <month>
```

**Examples:**
```
/report september
/report august
/report ijul
```

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
        "name": "YourCompany",
        "data": "Your Company Name\\nYour Address\\nBank Details"
    }
]
```

## Jira Work Reports

### Configuration

Add to `bot/config.env`:
```env
# Jira Configuration
JIRA_SERVER=https://your-company.atlassian.net
JIRA_USERNAME=your_username@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=PROJECT
REPORT_AUTHOR=Your Name
```

### Usage

#### Via Telegram Bot:
```
/report september
```

#### Via Command Line:
```bash
python jira_report_generator.py september
```

### Supported Month Formats:
- **English:** january, february, march, april, may, june, july, august, september, october, november, december
- **Abbreviations:** jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec
- **Russian (transliterated):** janvar, fevral, mart, aprel, maj, ijun, ijul, avgust, sentjabr, oktjabr, nojabr, dekabr

### How it Works:
1. Connects to Jira using API token
2. Searches for tasks where you participated (assignee, reporter, commented)
3. Uses template `resources/report_work_template.docx`
4. Replaces `MM` with month number, `yyyy` with year
5. Adds tasks in format `(<task>)<title_task>`
6. Saves to `reports/` directory

For detailed documentation, see [JIRA_REPORTS_GUIDE.md](JIRA_REPORTS_GUIDE.md).