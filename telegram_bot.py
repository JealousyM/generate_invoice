#!/usr/bin/env python3
"""
Telegram Bot for Invoice Generation (Version 21.8 compatible)
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from generate_invoice import InvoiceGenerator

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InvoiceTelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.allowed_users = self._parse_allowed_users()
        self.invoice_generator = InvoiceGenerator()
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in config.env")
    
    def _parse_allowed_users(self):
        """Parse allowed user IDs from environment"""
        users_str = os.getenv('ALLOWED_USER_IDS', '')
        if not users_str:
            return []
        
        try:
            return [int(user_id.strip()) for user_id in users_str.split(',') if user_id.strip()]
        except ValueError:
            logger.warning("Invalid ALLOWED_USER_IDS format")
            return []
    
    def _is_user_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to use the bot"""
        if not self.allowed_users:
            return True  # If no restrictions set, allow all users
        return user_id in self.allowed_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        if not self._is_user_allowed(user_id):
            await update.message.reply_text("❌ You don't have access to this bot.")
            return
        
        welcome_message = """
🏦 *Invoice Generator*

Available commands:

📄 `/generate <date> <end_date> <buyer> <recipient> <amount>`
Generates invoice with specified parameters

Example:
`/generate 04.09.2025 14/09/2025 Retano-Latvia Retano-Latvia 3000.00`

📋 `/help` \\- show this help
📊 `/status` \\- check system status
🏢 `/orgs` \\- show available organizations
        """
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📋 *Command Help:*

🔹 `/generate <date> <end_date> <buyer> <recipient> <amount>`
   Generates invoice with specified parameters
   
   *Date Format:*
   \\- Date: DD\\.MM\\.YYYY \\(example: 04\\.09\\.2025\\)
   \\- End Date: DD/MM/YYYY \\(example: 14/09/2025\\)
   
   *Example:*
   `/generate 04.09.2025 14/09/2025 Retano-Latvia Retano-Latvia 3000.00`

🔹 `/status` \\- Check system status
🔹 `/orgs` \\- Show available organizations
🔹 `/help` \\- Show this help

💡 *Tip:* Use commands exactly in the specified format for correct operation\\.
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        
        if not self._is_user_allowed(user_id):
            await update.message.reply_text("❌ You don't have access to this bot.")
            return
        
        # Check system status
        try:
            # Test invoice generator
            orgs_count = len(self.invoice_generator.orgs_data)
            
            # Check invoices directory
            invoices_dir = Path("invoices")
            invoices_count = len(list(invoices_dir.glob("*.docx"))) if invoices_dir.exists() else 0
            
            current_time = datetime.now().strftime('%d\\.%m\\.%Y %H:%M:%S')
            
            status_message = f"""
📊 *System Status:*

✅ Invoice Generator: Working
✅ Organizations in database: {orgs_count}
📁 Invoices created: {invoices_count}
🕐 Check time: {current_time}

🟢 System ready to work\\!
            """
            
        except Exception as e:
            current_time = datetime.now().strftime('%d\\.%m\\.%Y %H:%M:%S')
            error_msg = str(e).replace('.', '\\.')
            status_message = f"""
📊 *System Status:*

❌ Error: {error_msg}
🕐 Check time: {current_time}

🔴 System needs attention\\!
            """
        
        await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN_V2)
    
    async def orgs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /orgs command"""
        user_id = update.effective_user.id
        
        if not self._is_user_allowed(user_id):
            await update.message.reply_text("❌ You don't have access to this bot.")
            return
        
        try:
            orgs = self.invoice_generator.orgs_data
            
            if not orgs:
                await update.message.reply_text("📋 No organizations found in database.")
                return
            
            orgs_text = "🏢 *Available Organizations:*\n\n"
            
            for i, org in enumerate(orgs, 1):
                name = org.get('name', 'No name')
                data_preview = org.get('data', '')[:100] + '...' if len(org.get('data', '')) > 100 else org.get('data', '')
                
                # Escape markdown characters
                name = name.replace('.', '\\.')
                data_preview = data_preview.replace('.', '\\.')
                
                orgs_text += f"{i}\\. *{name}*\n"
                orgs_text += f"   {data_preview}\n\n"
            
            await update.message.reply_text(orgs_text, parse_mode=ParseMode.MARKDOWN_V2)
            
        except Exception as e:
            error_msg = str(e).replace('.', '\\.')
            await update.message.reply_text(f"❌ Error getting organizations list: {error_msg}")
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate command"""
        user_id = update.effective_user.id
        logger.info(f"Generate command called by user {user_id}")
        logger.info(f"Command args: {context.args}")
        
        if not self._is_user_allowed(user_id):
            await update.message.reply_text("❌ You don't have access to this bot.")
            return
        
        # Parse command arguments
        if len(context.args) != 5:
            await update.message.reply_text(
                "❌ Invalid command format\\!\n\n"
                "Use:\n"
                "`/generate <date> <end_date> <buyer> <recipient> <amount>`\n\n"
                "Example:\n"
                "`/generate 04\\.09\\.2025 14/09/2025 Retano\\-Latvia Retano\\-Latvia 3000\\.00`",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        date_str, end_date_str, buyer, recipient, amount = context.args
        
        # Send "processing" message
        processing_msg = await update.message.reply_text("⏳ Generating invoice...")
        
        try:
            # Generate invoice
            self.invoice_generator.generate_invoice(date_str, end_date_str, buyer, recipient, amount)
            
            # Check if files were created
            filename = f"Peraviortkin_Mi_code_{date_str}.docx"
            docx_path = Path("invoices") / filename
            
            if docx_path.exists():
                # Escape markdown characters for the success message
                escaped_filename = filename.replace('.', '\\.')
                escaped_date = date_str.replace('.', '\\.')
                escaped_end_date = end_date_str.replace('/', '\\/')
                escaped_buyer = buyer.replace('-', '\\-')
                escaped_recipient = recipient.replace('-', '\\-')
                escaped_amount = amount.replace('.', '\\.')
                
                # Send success message
                success_message = f"""
✅ *Invoice successfully created\\!*

📄 File: `{escaped_filename}`
📅 Date: {escaped_date}
📅 Deadline: {escaped_end_date}
🏢 Buyer: {escaped_buyer}
🏢 Recipient: {escaped_recipient}
💰 Amount: {escaped_amount} EUR

📁 File saved to invoices/ folder
                """
                
                await processing_msg.edit_text(success_message, parse_mode=ParseMode.MARKDOWN_V2)
                
                # Send the DOCX file
                try:
                    with open(docx_path, 'rb') as doc_file:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=doc_file,
                            filename=filename,
                            caption=f"📄 Invoice {filename}"
                        )
                except Exception as e:
                    await update.message.reply_text(f"⚠️ File created but failed to send: {str(e)}")
                
            else:
                await processing_msg.edit_text("❌ Error: invoice file was not created")
                
        except Exception as e:
            error_message = f"❌ Error generating invoice:\n`{str(e)}`"
            await processing_msg.edit_text(error_message, parse_mode=ParseMode.MARKDOWN_V2)
            logger.error(f"Invoice generation error: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_id = update.effective_user.id
        message_text = update.message.text
        logger.info(f"Message handler called by user {user_id}, text: '{message_text}'")
        
        if not self._is_user_allowed(user_id):
            return
        
        await update.message.reply_text(
            "💡 Use commands to work with the bot\\.\n"
            "Type /help for help\\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text("❌ Internal error occurred. Please try again later.")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Invoice Telegram Bot v21.8...")
        
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("orgs", self.orgs_command))
        application.add_handler(CommandHandler("generate", self.generate_command))
        
        # Add message handler for non-commands
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        logger.info("Bot is starting to poll for updates...")
        try:
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise

def main():
    """Main function"""
    print("🤖 Starting Telegram bot for invoice generation (v21.8)...")
    
    # Check if config file exists
    if not os.path.exists('config.env'):
        print("❌ config.env file not found!")
        print("📝 Run: python setup_bot.py")
        sys.exit(1)
    
    try:
        bot = InvoiceTelegramBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("📝 Check config.env file or run: python setup_bot.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.exception("Critical error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main()
