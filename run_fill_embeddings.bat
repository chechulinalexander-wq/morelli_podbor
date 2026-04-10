@echo off
chcp 65001 > nul
echo ========================================
echo Starting Handle Analysis with GPT-4 Vision
echo ========================================
echo.

python fill_handle_embeddings.py

echo.
echo ========================================
echo Process completed!
echo ========================================
pause
