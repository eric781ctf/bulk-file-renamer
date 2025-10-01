#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量檔案重命名工具
Bulk File Renamer Tool

一個功能豐富的桌面應用程式，用於批量重命名檔案
支援多種重命名規則和預覽功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import json
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from file_renamer import FileRenamer
from gui.main_window import MainWindow

def main():
    """主程式入口點"""
    try:
        # 創建主視窗
        root = tk.Tk()
        app = MainWindow(root)
        
        # 設定視窗關閉事件
        def on_closing():
            if messagebox.askokcancel("退出", "確定要退出批量檔案重命名工具嗎？"):
                app.save_settings()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 啟動應用程式
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("錯誤", f"應用程式啟動失敗：\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()