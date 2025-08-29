# 🤖 Telegram Bot Setup Guide for Invoice Generation

## Quick Start

### 1. 📋 Prerequisites
- Python 3.13+
- Telegram account
- Access to @BotFather in Telegram

### 2. 🔧 Telegram Bot Setup

#### Creating the Bot
1. Open Telegram and find @BotFather
2. Send command `/newbot`
3. Enter name for your bot (e.g., "Invoice Generator Bot")
4. Enter username (e.g., "your_invoice_bot")
5. **Save the token** (looks like `123456789:ABCDEF1234567890...`)

#### Getting Your User ID (optional)
1. Find @userinfobot in Telegram
2. Send `/start`
3. Copy your ID (e.g., `123456789`)

### 3. ⚙️ Installation and Setup

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Automatic Setup
```bash
python setup_bot.py
```

Follow the prompts:
- Enter your bot token
- Enter user IDs who can access the bot (optional)

#### Manual Setup
Create `config.env` file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_USER_IDS=123456789,987654321
DEFAULT_BUYER=Retano-Latvia
DEFAULT_RECIPIENT=Retano-Latvia
```

### 4. 🚀 Running the Bot

#### Start the Bot
```bash
python telegram_bot.py
```

#### Alternative: Auto-restart Runner
```bash
python run_bot.py
```

## 📱 Using the Bot

### Available Commands

#### `/start`
- Welcome message
- Shows available commands

#### `/help`
- Detailed command help
- Date format examples
- Usage examples

#### `/status`
- System status check
- Shows number of organizations
- Shows created invoices count

#### `/orgs`
- Lists available organizations
- Shows organization data

#### `/generate`
Generate invoice with parameters:
```
/generate <date> <end_date> <buyer> <recipient> <amount>
```

**Example:**
```
/generate 04.09.2025 14/09/2025 Retano-Latvia Retano-Latvia 3000.00
```

### Parameter Details

- **Date**: DD.MM.YYYY format (e.g., 04.09.2025)
- **End Date**: DD/MM/YYYY format (e.g., 14/09/2025)
- **Buyer**: Organization name from orgs.json
- **Recipient**: Organization name from orgs.json
- **Amount**: Number with decimal point (e.g., 3000.00)

## 🏢 Organization Configuration

Edit `orgs.json` to add your organizations:

```json
[
    {
        "name": "Retano-Latvia",
        "data": "RETANO SOLUTIONS LTD\\nVesetas 7, Riga, LATVIA\\nBank: АО Rietumu Banka\\nNr rachunku/ Bank account number: LV72RTMB0000700806618\\nSWIFT: RTMBLV2X"
    },
    {
        "name": "YourCompany",
        "data": "Your Company Name\\nYour Address\\nBank Details"
    }
]
```

## 🔧 Troubleshooting

### Bot Not Responding
1. Check bot token in `config.env`
2. Verify your User ID is in ALLOWED_USER_IDS
3. Check internet connection
4. Restart the bot

### Permission Denied
- Make sure your Telegram User ID is in the ALLOWED_USER_IDS list
- If ALLOWED_USER_IDS is empty, bot is open to everyone

### Invoice Generation Fails
1. Check if `invoice_template.docx` exists
2. Verify `orgs.json` contains valid organizations
3. Check `invoices/` directory exists and is writable

### Python/Library Issues
```bash
# Check Python version (should be 3.13+)
python --version

# Check if libraries are installed
pip show python-telegram-bot
pip show python-docx

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Version Compatibility
- **Python 3.13** required
- **python-telegram-bot 21.8** required
- Other versions may not work

## 🔒 Security Best Practices

### Protect Your Bot Token
- Never share your bot token publicly
- Keep `config.env` private
- Add `config.env` to `.gitignore`

### User Access Control
- Use ALLOWED_USER_IDS to restrict access
- Regularly review who has access
- Consider changing bot token periodically

### File Permissions
- Ensure `invoices/` directory has proper write permissions
- Keep sensitive files out of public directories

## 📊 File Structure
```
project/
├── 📄 invoice_template.docx    # Invoice template
├── 📊 orgs.json               # Organization data
├── 🤖 telegram_bot.py         # Main bot script
├── 🔧 generate_invoice.py     # CLI generator
├── ⚙️ setup_bot.py           # Setup script
├── 📋 requirements.txt        # Dependencies
├── 📝 config.env             # Bot configuration
├── 📂 invoices/              # Generated invoices
└── 📚 TELEGRAM_BOT_GUIDE.md  # This guide
```

## 🎯 Example Workflow

1. **Setup**: Run `python setup_bot.py`
2. **Start**: Run `python telegram_bot.py`
3. **Find Bot**: Search for your bot in Telegram
4. **Test**: Send `/start` to verify it works
5. **Generate**: Send `/generate 04.09.2025 14/09/2025 Retano-Latvia Retano-Latvia 3000.00`
6. **Download**: Bot will send you the generated DOCX file

## ❓ FAQ

### Q: Can I change the invoice template?
A: Yes, edit `invoice_template.docx` but keep the placeholders (`<dd>`, `<mm>`, etc.)

### Q: How do I add new organizations?
A: Edit `orgs.json` and add new organization objects

### Q: Can multiple people use the bot?
A: Yes, add their User IDs to ALLOWED_USER_IDS in `config.env`

### Q: What if I lose my bot token?
A: Contact @BotFather and use `/token` command to get a new one

### Q: Why doesn't PDF generation work?
A: PDF generation is disabled due to Python 3.13 compatibility issues. Use DOCX files or convert manually.

## 🐛 Reporting Issues

If you encounter problems:
1. Check this guide first
2. Verify your setup follows all steps
3. Check Python and library versions
4. Review bot logs for error messages

---

**Status**: ✅ Fully functional with Python 3.13 and python-telegram-bot 21.8