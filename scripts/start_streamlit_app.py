# -*- coding: utf-8 -*-
"""
Streamlit应用启动脚本
独立启动Streamlit应用，可与FastAPI并行运行
"""

import subprocess
import sys

if __name__ == "__main__":
    print("正在启动Streamlit应用...")
    print("服务地址: http://localhost:8501")
    print("-" * 50)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
