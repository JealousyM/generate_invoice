#!/usr/bin/env python3
"""
Test generate command specifically
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_invoice import InvoiceGenerator

# Load environment variables
load_dotenv('../config.env')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test generate command"""
    logger.info(f"Generate command received from user {update.effective_user.id}")
    logger.info(f"Args: {context.args}")
    
    await update.message.reply_text("🧪 Generate command received!")
    
    if len(context.args) != 5:
        await update.message.reply_text(f"❌ Invalid number of arguments: {len(context.args)}")
        return
    
    date_str, end_date_str, buyer, recipient, amount = context.args
    await update.message.reply_text(f"📋 Parameters:\n{date_str}, {end_date_str}, {buyer}, {recipient}, {amount}")
    
    try:
        # Create generator
        generator = InvoiceGenerator()
        await update.message.reply_text("⏳ Generating...")
        
        # Generate
        generator.generate_invoice(date_str, end_date_str, buyer, recipient, amount)
        
        # Check file
        filename = f"Peraviortkin_Mi_code_{date_str}.docx"
        docx_path = Path("../invoices") / filename
        
        if docx_path.exists():
            await update.message.reply_text(f"✅ File created: {filename}")
            
            # Send file
            with open(docx_path, 'rb') as doc_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=doc_file,
                    filename=filename,
                    caption=f"📄 Invoice {filename}"
                )
        else:
            await update.message.reply_text("❌ File not created")
            
    except Exception as e:
        logger.exception("Error in generate command")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text("🧪 Test bot started!\nUse: /generate 04.09.2025 14/09/2025 Organization Organization 3000.00")

def main():
    """Main function"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ Token not found!")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("generate", test_generate))
    
    print("🧪 Starting test bot...")
    application.run_polling()

if __name__ == "__main__":
    main()

