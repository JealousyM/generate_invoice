#!/usr/bin/env python3
"""
Convenience launcher for Bot Setup
"""

import os
import sys
from pathlib import Path

def main():
    """Launch the bot setup"""
    # Change to bot directory and run setup
    setup_script = Path("bot/setup_bot.py")
    
    if not setup_script.exists():
        print("❌ Setup script not found at bot/setup_bot.py")
        sys.exit(1)
    
    # Run the setup script
    os.system(f"{sys.executable} {setup_script}")

if __name__ == "__main__":
    main()

