#!/usr/bin/env python3
"""
Simple bot runner with restart capability
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_config():
    """Check if config file exists"""
    config_path = Path("../config.env")
    if not config_path.exists():
        print("❌ config.env file not found!")
        print("📝 Run: python bot/setup_bot.py")
        return False
    return True

def run_bot():
    """Run the telegram bot"""
    print("🤖 Starting Telegram bot...")
    
    try:
        # Run the bot
        result = subprocess.run([sys.executable, "telegram_bot.py"], check=True)
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Bot exited with error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function with restart logic"""
    if not check_config():
        sys.exit(1)
    
    restart_count = 0
    max_restarts = 5
    
    while restart_count < max_restarts:
        success = run_bot()
        
        if success:
            break
        
        restart_count += 1
        print(f"🔄 Restarting bot ({restart_count}/{max_restarts})")
        time.sleep(5)
    
    if restart_count >= max_restarts:
        print(f"❌ Maximum restart attempts exceeded ({max_restarts})")
        sys.exit(1)

if __name__ == "__main__":
    main()

