#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試腳本
Test Script for Bulk File Renamer
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# 添加源碼路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from file_renamer import FileRenamer, RenameRule

def create_test_files(test_dir, file_count=5):
    """創建測試檔案"""
    test_files = []
    for i in range(file_count):
        filename = f"test_file_{i+1}.txt"
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"這是測試檔案 {i+1}\n建立時間: {datetime.now()}")
        test_files.append(filename)
    
    # 創建一些不同類型的檔案
    extra_files = [
        "document.doc",
        "image.jpg", 
        "data.xlsx",
        "presentation.ppt"
    ]
    
    for filename in extra_files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"測試檔案: {filename}")
        test_files.append(filename)
    
    return test_files

def test_file_renamer():
    """測試檔案重命名功能"""
    print("=" * 50)
    print("批量檔案重命名工具 - 功能測試")
    print("=" * 50)
    
    # 創建臨時測試目錄
    test_dir = tempfile.mkdtemp(prefix="bulk_renamer_test_")
    print(f"測試目錄: {test_dir}")
    
    try:
        # 創建測試檔案
        print("\n1. 創建測試檔案...")
        test_files = create_test_files(test_dir)
        print(f"   已創建 {len(test_files)} 個測試檔案")
        
        # 初始化重命名器
        print("\n2. 初始化檔案重命名器...")
        renamer = FileRenamer()
        renamer.set_source_directory(test_dir)
        print(f"   載入了 {len(renamer.files_list)} 個檔案")
        
        # 測試前綴規則
        print("\n3. 測試前綴規則...")
        rule1 = RenameRule()
        rule1.rule_type = "prefix"
        rule1.prefix = "新_"
        renamer.add_rename_rule(rule1)
        
        preview = renamer.preview_rename()
        print("   預覽結果:")
        for result in preview[:3]:  # 只顯示前3個
            print(f"     {result['original_name']} → {result['new_name']}")
        
        # 執行重命名
        print("\n4. 執行重命名...")
        success, error, errors = renamer.execute_rename(preview)
        print(f"   成功: {success} 個, 失敗: {error} 個")
        if errors:
            print(f"   錯誤: {errors[:2]}")  # 只顯示前2個錯誤
        
        # 測試復原功能
        print("\n5. 測試復原功能...")
        if renamer.undo_last_operation():
            print("   復原成功!")
        else:
            print("   復原失敗!")
        
        # 測試序列編號規則
        print("\n6. 測試序列編號規則...")
        renamer.clear_rename_rules()
        rule2 = RenameRule()
        rule2.rule_type = "sequence"
        rule2.sequence_start = 1
        rule2.sequence_digits = 3
        renamer.add_rename_rule(rule2)
        
        # 設定檔案過濾器 - 只處理 .txt 檔案
        renamer.set_file_filters(['.txt'])
        
        preview = renamer.preview_rename()
        print("   序列編號預覽 (僅 .txt 檔案):")
        for result in preview[:3]:
            print(f"     {result['original_name']} → {result['new_name']}")
        
        # 測試替換規則
        print("\n7. 測試文字替換規則...")
        renamer.clear_rename_rules()
        renamer.set_file_filters([])  # 清除過濾器
        
        rule3 = RenameRule()
        rule3.rule_type = "replace"
        rule3.find_text = "test"
        rule3.replace_text = "demo"
        rule3.include_extension = False
        renamer.add_rename_rule(rule3)
        
        preview = renamer.preview_rename()
        print("   文字替換預覽:")
        for result in preview[:3]:
            print(f"     {result['original_name']} → {result['new_name']}")
        
        # 測試大小寫轉換
        print("\n8. 測試大小寫轉換...")
        renamer.clear_rename_rules()
        
        rule4 = RenameRule()
        rule4.rule_type = "case"
        rule4.case_option = "upper"
        renamer.add_rename_rule(rule4)
        
        preview = renamer.preview_rename()
        print("   大小寫轉換預覽:")
        for result in preview[:3]:
            print(f"     {result['original_name']} → {result['new_name']}")
        
        print("\n✅ 所有功能測試完成!")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理測試目錄
        try:
            shutil.rmtree(test_dir)
            print(f"\n🧹 已清理測試目錄: {test_dir}")
        except Exception as e:
            print(f"\n⚠️ 清理測試目錄時發生錯誤: {e}")

def test_gui_import():
    """測試 GUI 模組匯入"""
    print("\n" + "=" * 50)
    print("GUI 模組匯入測試")
    print("=" * 50)
    
    try:
        print("測試匯入 tkinter...")
        import tkinter as tk
        print("✅ tkinter 匯入成功")
        
        print("測試匯入主視窗...")
        from src.gui.main_window import MainWindow
        print("✅ MainWindow 匯入成功")
        
        print("測試匯入規則面板...")
        from src.gui.rule_panel import RulePanel
        print("✅ RulePanel 匯入成功")
        
        print("測試匯入預覽面板...")
        from src.gui.preview_panel import PreviewPanel
        print("✅ PreviewPanel 匯入成功")
        
        print("測試匯入歷史面板...")
        from src.gui.history_panel import HistoryPanel
        print("✅ HistoryPanel 匯入成功")
        
        print("\n✅ 所有 GUI 模組匯入成功!")
        
    except Exception as e:
        print(f"\n❌ GUI 模組匯入失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 測試核心功能
    test_file_renamer()
    
    # 測試 GUI 匯入
    test_gui_import()
    
    print("\n" + "=" * 50)
    print("測試完成! 您現在可以執行 'python main.py' 來啟動應用程式")
    print("=" * 50)