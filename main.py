import streamlit as st
import subprocess
import sys

if __name__ == "__main__":
    # Run the main dashboard
    subprocess.run([sys.executable, "-m", "streamlit", "run", "cardgenius_dashboard.py"])

