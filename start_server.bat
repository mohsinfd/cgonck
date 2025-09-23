@echo off
echo Starting CardGenius Dashboard Server...
echo.
echo Server will be available at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
python -m streamlit run cardgenius_dashboard.py --server.port 8501
pause

