#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主視窗界面
Main Window GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.file_renamer import FileRenamer, RenameRule
from src.gui.rule_panel import RulePanel
from src.gui.preview_panel import PreviewPanel
from src.gui.history_panel import HistoryPanel

class MainWindow:
    """主視窗類別"""
    
    def __init__(self, root):
        self.root = root
        self.file_renamer = FileRenamer()
        self.file_renamer.load_history()
        
        self.setup_window()
        self.create_widgets()
        self.load_settings()
    
    def setup_window(self):
        """設定視窗屬性"""
        self.root.title("批量檔案重命名工具 v1.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 設定圖示（如果有的話）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 設定樣式
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """創建界面組件"""
        # 創建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 創建頂部工具欄
        self.create_toolbar(main_frame)
        
        # 創建主要內容區域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 創建筆記本控件（分頁）
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 創建各個分頁
        self.create_main_tab()
        self.create_history_tab()
        
        # 創建狀態欄
        self.create_statusbar(main_frame)
    
    def create_toolbar(self, parent):
        """創建工具欄"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 目錄選擇區域
        dir_frame = ttk.LabelFrame(toolbar_frame, text="目錄設定", padding=10)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 目錄路徑顯示
        self.dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, state='readonly')
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 瀏覽按鈕
        browse_btn = ttk.Button(dir_frame, text="瀏覽目錄", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT)
        
        # 快速操作按鈕
        action_frame = ttk.Frame(toolbar_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="預覽重命名", command=self.preview_rename).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="執行重命名", command=self.execute_rename).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="復原操作", command=self.undo_operation).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="刷新列表", command=self.refresh_files).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_main_tab(self):
        """創建主要操作分頁"""
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="檔案重命名")
        
        # 創建水平分割器
        paned_window = ttk.PanedWindow(main_tab, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左側：規則設定面板
        self.rule_panel = RulePanel(paned_window, self.file_renamer)
        paned_window.add(self.rule_panel.frame, weight=1)
        
        # 右側：預覽面板
        self.preview_panel = PreviewPanel(paned_window, self.file_renamer)
        paned_window.add(self.preview_panel.frame, weight=2)
    
    def create_history_tab(self):
        """創建歷史記錄分頁"""
        history_tab = ttk.Frame(self.notebook)
        self.notebook.add(history_tab, text="操作歷史")
        
        # 歷史記錄面板
        self.history_panel = HistoryPanel(history_tab, self.file_renamer)
    
    def create_statusbar(self, parent):
        """創建狀態欄"""
        statusbar_frame = ttk.Frame(parent)
        statusbar_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 狀態標籤
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        status_label = ttk.Label(statusbar_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # 檔案計數標籤
        self.file_count_var = tk.StringVar()
        self.file_count_var.set("檔案數量: 0")
        count_label = ttk.Label(statusbar_frame, textvariable=self.file_count_var)
        count_label.pack(side=tk.RIGHT)
    
    def browse_directory(self):
        """瀏覽並選擇目錄"""
        directory = filedialog.askdirectory(
            title="選擇要處理的目錄",
            initialdir=self.file_renamer.settings.get('last_directory', '')
        )
        
        if directory:
            if self.file_renamer.set_source_directory(directory):
                self.dir_var.set(directory)
                self.update_file_count()
                self.preview_panel.refresh_preview()
                self.status_var.set(f"已載入目錄: {os.path.basename(directory)}")
                
                # 儲存最後使用的目錄
                self.file_renamer.settings['last_directory'] = directory
            else:
                messagebox.showerror("錯誤", "無法讀取指定的目錄")
    
    def preview_rename(self):
        """預覽重命名結果"""
        if not self.file_renamer.source_directory:
            messagebox.showwarning("警告", "請先選擇要處理的目錄")
            return
        
        if not self.file_renamer.rename_rules:
            messagebox.showwarning("警告", "請先設定重命名規則")
            return
        
        try:
            self.status_var.set("正在生成預覽...")
            self.root.update()
            
            self.preview_panel.refresh_preview()
            self.status_var.set("預覽已更新")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"預覽時發生錯誤:\n{str(e)}")
            self.status_var.set("預覽失敗")
    
    def execute_rename(self):
        """執行重命名操作"""
        if not self.file_renamer.source_directory:
            messagebox.showwarning("警告", "請先選擇要處理的目錄")
            return
        
        if not self.file_renamer.rename_rules:
            messagebox.showwarning("警告", "請先設定重命名規則")
            return
        
        # 獲取預覽結果
        preview_results = self.file_renamer.preview_rename()
        
        if not preview_results:
            messagebox.showinfo("資訊", "沒有檔案需要重命名")
            return
        
        # 檢查是否有衝突
        conflicts = [r for r in preview_results if r['conflict']]
        if conflicts:
            if not messagebox.askyesno("警告", 
                                     f"發現 {len(conflicts)} 個檔案存在衝突，"
                                     f"這些檔案將被跳過。\n是否繼續執行重命名？"):
                return
        
        # 確認執行
        total_files = len([r for r in preview_results if not r['conflict']])
        if not messagebox.askyesno("確認", 
                                 f"即將重命名 {total_files} 個檔案，"
                                 f"此操作無法自動復原。\n是否確定執行？"):
            return
        
        try:
            self.status_var.set("正在執行重命名...")
            self.root.update()
            
            success_count, error_count, errors = self.file_renamer.execute_rename(preview_results)
            
            # 顯示結果
            if errors:
                error_msg = "\n".join(errors[:10])  # 只顯示前10個錯誤
                if len(errors) > 10:
                    error_msg += f"\n... 以及其他 {len(errors) - 10} 個錯誤"
                
                messagebox.showwarning("完成（有錯誤）", 
                                     f"重命名完成！\n"
                                     f"成功: {success_count} 個檔案\n"
                                     f"失敗: {error_count} 個檔案\n\n"
                                     f"錯誤詳情:\n{error_msg}")
            else:
                messagebox.showinfo("完成", f"重命名完成！\n成功處理 {success_count} 個檔案")
            
            # 更新界面
            self.preview_panel.refresh_preview()
            self.history_panel.refresh_history()
            self.update_file_count()
            self.status_var.set(f"重命名完成 - 成功: {success_count}, 失敗: {error_count}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"執行重命名時發生錯誤:\n{str(e)}")
            self.status_var.set("重命名失敗")
    
    def undo_operation(self):
        """復原上一次操作"""
        if not self.file_renamer.history:
            messagebox.showinfo("資訊", "沒有可復原的操作")
            return
        
        last_operation = self.file_renamer.history[-1]
        operation_count = len(last_operation['operations'])
        operation_time = last_operation['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        if not messagebox.askyesno("確認復原", 
                                 f"即將復原以下操作：\n"
                                 f"時間: {operation_time}\n"
                                 f"檔案數量: {operation_count}\n"
                                 f"目錄: {last_operation['directory']}\n\n"
                                 f"是否確定復原？"):
            return
        
        try:
            self.status_var.set("正在復原操作...")
            self.root.update()
            
            if self.file_renamer.undo_last_operation():
                messagebox.showinfo("完成", f"成功復原 {operation_count} 個檔案的重命名")
                
                # 更新界面
                self.preview_panel.refresh_preview()
                self.history_panel.refresh_history()
                self.update_file_count()
                self.status_var.set("復原操作完成")
            else:
                messagebox.showerror("錯誤", "復原操作失敗")
                self.status_var.set("復原失敗")
                
        except Exception as e:
            messagebox.showerror("錯誤", f"復原操作時發生錯誤:\n{str(e)}")
            self.status_var.set("復原失敗")
    
    def refresh_files(self):
        """刷新檔案列表"""
        if self.file_renamer.source_directory:
            self.file_renamer.refresh_files_list()
            self.preview_panel.refresh_preview()
            self.update_file_count()
            self.status_var.set("檔案列表已刷新")
        else:
            messagebox.showwarning("警告", "請先選擇要處理的目錄")
    
    def update_file_count(self):
        """更新檔案計數顯示"""
        total_files = len(self.file_renamer.files_list)
        filtered_files = len(self.file_renamer.filtered_files)
        
        if total_files == filtered_files:
            self.file_count_var.set(f"檔案數量: {total_files}")
        else:
            self.file_count_var.set(f"檔案數量: {filtered_files}/{total_files}")
    
    def load_settings(self):
        """載入程式設定"""
        try:
            settings = self.file_renamer.settings
            
            # 載入視窗幾何
            if 'window_geometry' in settings:
                self.root.geometry(settings['window_geometry'])
            
            # 載入最後使用的目錄
            if 'last_directory' in settings and settings['last_directory']:
                if os.path.exists(settings['last_directory']):
                    self.file_renamer.set_source_directory(settings['last_directory'])
                    self.dir_var.set(settings['last_directory'])
                    self.update_file_count()
                    
        except Exception as e:
            print(f"載入設定時發生錯誤: {e}")
    
    def save_settings(self):
        """儲存程式設定"""
        try:
            settings = self.file_renamer.settings
            
            # 儲存視窗幾何
            settings['window_geometry'] = self.root.geometry()
            
            # 儲存目前目錄
            settings['last_directory'] = self.file_renamer.source_directory
            
            self.file_renamer.save_settings(settings)
            
        except Exception as e:
            print(f"儲存設定時發生錯誤: {e}")