#!/usr/bin/env python3
"""
Setup script for Telegram Invoice Bot
"""

import os
import sys
from pathlib import Path

def create_config_file():
    """Create configuration file if it doesn't exist"""
    config_path = Path("../config.env")
    
    if config_path.exists():
        print("✅ config.env file already exists")
        return True
    
    print("📝 Creating configuration file...")
    
    # Get bot token from user
    bot_token = input("🤖 Enter Telegram bot token (get from @BotFather): ").strip()
    
    if not bot_token:
        print("❌ Bot token is required!")
        return False
    
    # Get allowed users (optional)
    print("\n👥 Access setup (optional):")
    print("   If no users specified, bot will be available to everyone")
    user_ids = input("   Enter user IDs comma-separated (or Enter to skip): ").strip()
    
    # Create config content
    config_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={bot_token}
ALLOWED_USER_IDS={user_ids}

# Invoice Configuration  
DEFAULT_BUYER=organization
DEFAULT_RECIPIENT=organization
"""
    
    # Write config file
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ Configuration saved to {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating configuration: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'telegram',
        'python-dotenv',
        'docx',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'docx':
                import docx
            elif package == 'telegram':
                import telegram
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'requests':
                import requests
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📥 Install dependencies: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def check_invoice_system():
    """Check if invoice generation system works"""
    print("🏦 Checking invoice generation system...")
    
    try:
        # Add parent directory to path for imports
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from generate_invoice import InvoiceGenerator
        
        generator = InvoiceGenerator()
        orgs_count = len(generator.orgs_data)
        
        print(f"✅ Invoice system working (organizations: {orgs_count})")
        return True
        
    except Exception as e:
        print(f"❌ Invoice system error: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating necessary folders...")
    
    directories = ["../invoices"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created folder: {dir_name}")
        else:
            print(f"✅ Folder already exists: {dir_name}")

def main():
    """Main setup function"""
    print("🚀 Setting up Telegram bot for invoice generation")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Install dependencies and run setup again")
        sys.exit(1)
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Check invoice system
    if not check_invoice_system():
        print("\n❌ Issues with invoice generation system")
        sys.exit(1)
    
    # Step 4: Create config
    if not create_config_file():
        print("\n❌ Failed to create configuration")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 What's next:")
    print("1. Start the bot: python bot/telegram_bot.py")
    print("2. Find your bot in Telegram")
    print("3. Send /start command")
    print("4. Use /help for help")
    
    print("\n💡 Generation command example:")
    print("/generate 04.09.2025 14/09/2025 Organization Organization 3000.00")

if __name__ == "__main__":
    main()

