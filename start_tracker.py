#!/usr/bin/env python3
"""
💸 Personal Wealth Tracker Launcher
Quick start script for Tyler's wealth tracking app
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("🚀 Starting Personal Wealth Tracker...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Make sure you're in the correct directory.")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import streamlit
        import yfinance
        import plotly
        import pandas
        print("✅ All dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("🌐 Launching Streamlit app...")
    print("📊 Your wealth tracker will open at: http://localhost:8501")
    print("📥 CSV Import: Drag & drop your real SoFi/Fidelity/Robinhood data")
    print("🔄 Auto-refresh is available in the sidebar")
    print("💡 Tip: Load demo data to see all features in action")
    print("🏦 SoFi Integration: Setup .env file for auto-sync")
    print("=" * 50)
    
    # Start streamlit
    try:
        # Auto-open browser after short delay
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8501")
        
        import threading
        threading.Thread(target=open_browser).start()
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\n👋 Wealth Tracker stopped. Your data is saved locally.")
    except Exception as e:
        print(f"❌ Error starting app: {e}")

if __name__ == "__main__":
    main() 