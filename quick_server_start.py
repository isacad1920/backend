"""
Quick fix script to restore functionality for testing.
"""

import subprocess
import sys


def start_server():
    """Start the development server."""
    try:
        # Kill any existing process on port 8000
        subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True, check=False)
        subprocess.run(['kill', '-9'] + subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True).stdout.strip().split(), 
                      capture_output=True, check=False)
        
        print("🚀 Starting SOFinance server...")
        # Start the server
        subprocess.run([sys.executable, 'run.py'], check=True)
        
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()
