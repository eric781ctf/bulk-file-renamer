#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速啟動測試
Quick Start Test
"""

import sys
import os

def test_imports():
    """測試所有必要的匯入"""
    print("🔍 檢查模組匯入...")
    
    try:
        # 測試標準庫
        import tkinter as tk
        print("✅ tkinter 可用")
        
        import json
        print("✅ json 可用")
        
        import os
        print("✅ os 可用")
        
        import re
        print("✅ re 可用")
        
        from datetime import datetime
        print("✅ datetime 可用")
        
        # 測試專案模組
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from file_renamer import FileRenamer, RenameRule
        print("✅ FileRenamer 可用")
        
        # 測試 GUI 模組
        from gui.main_window import MainWindow
        print("✅ MainWindow 可用")
        
        print("\n🎉 所有模組測試通過!")
        return True
        
    except Exception as e:
        print(f"\n❌ 模組測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_demo_window():
    """創建示範視窗"""
    print("\n🚀 啟動圖形界面...")
    
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        # 創建主視窗
        root = tk.Tk()
        root.title("批量檔案重命名工具 - 啟動測試")
        root.geometry("600x400")
        root.resizable(True, True)
        
        # 創建內容
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        title_label = ttk.Label(main_frame, text="批量檔案重命名工具", 
                               font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 功能說明
        features_text = """
🎯 主要功能：
• 前綴/後綴添加
• 文字替換
• 序列編號
• 大小寫轉換
• 檔案過濾

📋 特色：
• 即時預覽
• 衝突檢測
• 操作歷史
• 一鍵復原

🛡️ 安全：
• 完整備份記錄
• 錯誤處理
• 操作確認
        """
        
        features_label = ttk.Label(main_frame, text=features_text, 
                                  font=("Microsoft YaHei", 10))
        features_label.pack(pady=(0, 20))
        
        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        def start_main_app():
            root.destroy()
            # 啟動主應用程式
            try:
                from gui.main_window import MainWindow
                from file_renamer import FileRenamer
                
                main_root = tk.Tk()
                app = MainWindow(main_root)
                main_root.mainloop()
                
            except Exception as e:
                messagebox.showerror("錯誤", f"啟動主應用程式失敗:\n{str(e)}")
        
        def show_about():
            about_text = """批量檔案重命名工具 v1.0.0

這是一個功能豐富的桌面應用程式，用於批量重命名檔案。

🔧 技術棧：
• Python 3.7+
• tkinter (GUI)
• 標準庫

📝 授權：MIT License
💡 開源項目，歡迎貢獻！"""
            messagebox.showinfo("關於", about_text)
        
        # 按鈕
        ttk.Button(button_frame, text="啟動主程式", 
                  command=start_main_app).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="關於", 
                  command=show_about).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="退出", 
                  command=root.quit).pack(side=tk.LEFT)
        
        # 狀態列
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)
        
        status_label = ttk.Label(status_frame, text="✅ 系統檢查通過，準備就緒", 
                                foreground="green")
        status_label.pack()
        
        # 運行
        root.mainloop()
        
    except Exception as e:
        print(f"❌ GUI 創建失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("批量檔案重命名工具 - 啟動測試")
    print("=" * 40)
    
    # 測試匯入
    if test_imports():
        # 創建測試視窗
        create_demo_window()
    else:
        print("\n❌ 環境檢查失敗，請檢查 Python 環境和依賴套件")
        input("按 Enter 鍵退出...")