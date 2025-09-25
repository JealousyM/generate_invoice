#!/usr/bin/env python3
"""
Telegram Bot for Invoice Generation (Version 21.8 compatible)
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Set

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_invoice import InvoiceGenerator
from gmail_listener import GmailListener, EmailPayload

# Load environment variables
load_dotenv('../config.env')

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
        self.gmail_listener = GmailListener(logger=logger)
        self.gmail_enabled = self.gmail_listener.is_configured()
        self._subscribed_chats: Set[int] = set()
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in config.env")

        if self.gmail_enabled:
            logger.info(
                "Gmail listener enabled (correspondents: %s | interval: %ss)",
                ", ".join(sorted(self.gmail_listener.correspondents)) or "none",
                self.gmail_listener.interval,
            )
        else:
            logger.info("Gmail listener disabled (missing configuration)")
    
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

        if update.effective_chat:
            self._subscribed_chats.add(update.effective_chat.id)
        
        welcome_message = """
🏦 *Invoice Generator*

Available commands:

📄 `/generate <date> <end_date> <buyer> <recipient> <amount>`
Generates invoice with specified parameters

Example:
`/generate 04.09.2025 14/09/2025 Organization Organization 3000.00`

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
   `/generate 04.09.2025 14/09/2025 Organization Organization 3000.00`

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
            invoices_dir = Path("../invoices")
            invoices_count = len(list(invoices_dir.glob("*.docx"))) if invoices_dir.exists() else 0
            
            current_time = datetime.now().strftime('%d\\.%m\\.%Y %H:%M:%S')
            
            gmail_status = "Enabled" if self.gmail_enabled else "Disabled"
            gmail_status = gmail_status.replace('.', '\\.')
            gmail_tracking = len(self.gmail_listener.correspondents)
            gmail_tracking_text = (
                f"tracked {gmail_tracking} addresses" if gmail_tracking else "no tracked addresses"
            )
            gmail_tracking_text = gmail_tracking_text.replace('.', '\\.')

            status_message = f"""
📊 *System Status:*

✅ Invoice Generator: Working
✅ Organizations in database: {orgs_count}
📁 Invoices created: {invoices_count}
📬 Gmail listener: {gmail_status} ({gmail_tracking_text})
🕐 Check time: {current_time}

🟢 System ready to work\!
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
                
                # Escape markdown characters for Markdown V2
                name = name.replace('\\', '\\\\').replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')
                data_preview = data_preview.replace('\\', '\\\\').replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')
                
                orgs_text += f"{i}\\. *{name}*\n"
                orgs_text += f"   {data_preview}\n\n"
            
            await update.message.reply_text(orgs_text, parse_mode=ParseMode.MARKDOWN_V2)
            
        except Exception as e:
            error_msg = str(e).replace('.', '\\.')
            await update.message.reply_text(f"❌ Error getting organizations list: {error_msg}")
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate command"""
        user_id = update.effective_user.id
        logger.info(f"=== GENERATE COMMAND HANDLER CALLED ===")
        logger.info(f"Generate command called by user {user_id}")
        logger.info(f"Command args: {context.args}")
        logger.info(f"Message text: {update.message.text}")
        
        if not self._is_user_allowed(user_id):
            logger.warning(f"User {user_id} not allowed. Allowed users: {self.allowed_users}")
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
            docx_path = Path("../invoices") / filename
            
            # Log the paths for debugging
            logger.info(f"Looking for invoice file: {docx_path}")
            logger.info(f"File exists: {docx_path.exists()}")
            logger.info(f"Absolute path: {docx_path.absolute()}")
            
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
    
    async def debug_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug handler to catch unhandled commands"""
        user_id = update.effective_user.id
        message_text = update.message.text
        logger.error(f"=== UNHANDLED COMMAND CAUGHT BY DEBUG HANDLER ===")
        logger.error(f"Command: '{message_text}' from user {user_id}")
        logger.error(f"This command was not handled by specific command handlers!")
        
        await update.message.reply_text(
            f"🐛 Debug: Command '{message_text}' was not handled by specific handlers\\!",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages (manually filter out commands)"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Manual command filtering - ignore all commands
        if message_text and message_text.startswith('/'):
            logger.info(f"Command '{message_text}' received by message handler - ignoring (will be handled by command handlers)")
            return
        
        logger.info(f"Non-command message handler called by user {user_id}, text: '{message_text}'")
        
        if not self._is_user_allowed(user_id):
            logger.warning(f"User {user_id} not in allowed list: {self.allowed_users}")
            return

        if update.effective_chat:
            self._subscribed_chats.add(update.effective_chat.id)

        await update.message.reply_text(
            "💡 Use commands to work with the bot\.\n"
            "Type /help for help\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text("❌ Internal error occurred. Please try again later.")

    async def _notify_email(self, bot, payload: EmailPayload):
        """Dispatch Gmail notification to known chat IDs."""

        message_text = self.gmail_listener.format_notification(payload)

        targets: Set[int] = set(self._subscribed_chats)
        if not targets and self.allowed_users:
            targets.update(self.allowed_users)

        if not targets:
            logger.warning(
                "Email UID %s ready but no chat IDs registered for notifications", payload.uid
            )
            return

        for chat_id in targets:
            try:
                await bot.send_message(chat_id=chat_id, text=message_text)
            except Exception as exc:
                logger.error("Failed to send email notification to chat %s: %s", chat_id, exc)
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Invoice Telegram Bot v21.8...")
        
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add command handlers
        logger.info("Registering command handlers...")
        application.add_handler(CommandHandler("start", self.start_command))
        logger.info("Registered /start command")
        application.add_handler(CommandHandler("help", self.help_command))
        logger.info("Registered /help command")
        application.add_handler(CommandHandler("status", self.status_command))
        logger.info("Registered /status command")
        application.add_handler(CommandHandler("orgs", self.orgs_command))
        logger.info("Registered /orgs command")
        application.add_handler(CommandHandler("generate", self.generate_command))
        logger.info("Registered /generate command")
        
        # Add catch-all command handler for debugging
        application.add_handler(MessageHandler(filters.COMMAND, self.debug_command_handler))
        logger.info("Registered debug command handler")
        
        # Add message handler for non-commands (manual filter to avoid filters.COMMAND issues)
        logger.info("Registering message handler for non-commands")
        application.add_handler(MessageHandler(filters.TEXT, self.handle_message), group=1)
        logger.info("Message handler registered with group=1 (manual command filtering)")
        
        # Add error handler
        application.add_error_handler(self.error_handler)

        if self.gmail_enabled:
            logger.info("Scheduling Gmail listener job (interval: %ss)", self.gmail_listener.interval)
            application.job_queue.run_repeating(
                self.gmail_listener.job_handler,
                interval=self.gmail_listener.interval,
                first=5,
                name="gmail-listener",
                data={"notify": self._notify_email},
            )
        else:
            logger.info("Gmail listener not scheduled (disabled)")
        
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
    if not os.path.exists('../config.env'):
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

