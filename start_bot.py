#!/usr/bin/env python3
"""
Convenience launcher for Telegram Bot
"""

import os
import sys
from pathlib import Path

def main():
    """Launch the telegram bot"""
    # Change to bot directory and run
    bot_script = Path("bot/telegram_bot.py")
    
    if not bot_script.exists():
        print("❌ Bot script not found at bot/telegram_bot.py")
        sys.exit(1)
    
    # Change to bot directory and run the script
    original_dir = os.getcwd()
    try:
        os.chdir("bot")
        os.system(f"{sys.executable} telegram_bot.py")
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    main()

