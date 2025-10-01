#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
預覽面板
Preview Panel
"""

import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime

class PreviewPanel:
    """預覽面板類別"""
    
    def __init__(self, parent, file_renamer):
        self.parent = parent
        self.file_renamer = file_renamer
        
        # 創建主框架
        self.frame = ttk.LabelFrame(parent, text="重命名預覽", padding=10)
        
        self.create_widgets()
        self.preview_results = []
    
    def create_widgets(self):
        """創建界面組件"""
        # 工具欄
        toolbar_frame = ttk.Frame(self.frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="刷新預覽", command=self.refresh_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="全選", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="反選", command=self.invert_selection).pack(side=tk.LEFT, padx=(0, 5))
        
        # 統計資訊
        self.stats_var = tk.StringVar()
        stats_label = ttk.Label(toolbar_frame, textvariable=self.stats_var)
        stats_label.pack(side=tk.RIGHT)
        
        # 創建樹狀檢視
        columns = ('new_name', 'size', 'modified', 'status')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='tree headings')
        
        # 設定欄位標題
        self.tree.heading('#0', text='原檔名')
        self.tree.heading('new_name', text='新檔名')
        self.tree.heading('size', text='大小')
        self.tree.heading('modified', text='修改時間')
        self.tree.heading('status', text='狀態')
        
        # 設定欄位寬度
        self.tree.column('#0', width=200)
        self.tree.column('new_name', width=200)
        self.tree.column('size', width=80)
        self.tree.column('modified', width=120)
        self.tree.column('status', width=100)
        
        # 創建滾動條
        v_scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 排列組件
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # 設定網格權重
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # 綁定事件
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)
        
        # 創建右鍵選單
        self.create_context_menu()
        
        # 詳細資訊框架
        details_frame = ttk.LabelFrame(self.frame, text="檔案詳細資訊", padding=10)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.details_text = tk.Text(details_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 綁定選擇事件
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_changed)
    
    def create_context_menu(self):
        """創建右鍵選單"""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="查看詳細資訊", command=self.show_file_details)
        self.context_menu.add_command(label="在檔案總管中顯示", command=self.show_in_explorer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="排除此檔案", command=self.exclude_file)
        self.context_menu.add_command(label="僅處理此檔案", command=self.include_only_this)
    
    def refresh_preview(self):
        """刷新預覽"""
        # 清除現有項目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.file_renamer.source_directory:
            self.update_stats(0, 0, 0)
            return
        
        try:
            # 獲取預覽結果
            self.preview_results = self.file_renamer.preview_rename()
            
            # 統計資訊
            total_files = len(self.preview_results)
            changed_files = 0
            conflict_files = 0
            
            # 添加項目到樹狀檢視
            for result in self.preview_results:
                original_name = result['original_name']
                new_name = result['new_name']
                size = self.format_file_size(result['size'])
                modified = result['modified'].strftime("%Y-%m-%d %H:%M")
                
                # 確定狀態
                if result['conflict']:
                    status = f"衝突: {result['conflict_reason']}"
                    conflict_files += 1
                    tag = 'conflict'
                elif original_name != new_name:
                    status = "將重命名"
                    changed_files += 1
                    tag = 'changed'
                else:
                    status = "無變化"
                    tag = 'unchanged'
                
                # 插入項目
                item = self.tree.insert('', 'end', text=original_name,
                                      values=(new_name, size, modified, status),
                                      tags=(tag,))
            
            # 設定標籤顏色
            self.tree.tag_configure('conflict', foreground='red')
            self.tree.tag_configure('changed', foreground='blue')
            self.tree.tag_configure('unchanged', foreground='gray')
            
            # 更新統計
            self.update_stats(total_files, changed_files, conflict_files)
            
        except Exception as e:
            print(f"刷新預覽時發生錯誤: {e}")
            self.update_stats(0, 0, 0)
    
    def format_file_size(self, size_bytes):
        """格式化檔案大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        size = float(size_bytes)
        i = 0
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def update_stats(self, total, changed, conflicts):
        """更新統計資訊"""
        if total == 0:
            self.stats_var.set("無檔案")
        else:
            self.stats_var.set(f"總計: {total} | 將變更: {changed} | 衝突: {conflicts}")
    
    def select_all(self):
        """全選所有項目"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def invert_selection(self):
        """反選"""
        selected = set(self.tree.selection())
        all_items = set(self.tree.get_children())
        
        # 清除當前選擇
        self.tree.selection_remove(*selected)
        
        # 選擇未選中的項目
        unselected = all_items - selected
        if unselected:
            self.tree.selection_add(*unselected)
    
    def on_double_click(self, event):
        """雙擊事件"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.show_file_details()
    
    def on_right_click(self, event):
        """右鍵點擊事件"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_selection_changed(self, event):
        """選擇改變事件"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            self.show_item_details(item)
        else:
            self.clear_details()
    
    def show_item_details(self, item):
        """顯示項目詳細資訊"""
        try:
            # 獲取項目資訊
            original_name = self.tree.item(item, 'text')
            values = self.tree.item(item, 'values')
            
            if len(values) >= 4:
                new_name, size, modified, status = values
                
                # 尋找對應的預覽結果
                result = None
                for r in self.preview_results:
                    if r['original_name'] == original_name:
                        result = r
                        break
                
                if result:
                    details = f"原檔名: {original_name}\n"
                    details += f"新檔名: {new_name}\n"
                    details += f"檔案大小: {size}\n"
                    details += f"修改時間: {modified}\n"
                    details += f"狀態: {status}\n"
                    details += f"完整路徑: {result['full_path']}\n"
                    
                    if result['conflict']:
                        details += f"衝突原因: {result['conflict_reason']}\n"
                    
                    self.update_details(details)
                else:
                    self.clear_details()
            else:
                self.clear_details()
                
        except Exception as e:
            print(f"顯示詳細資訊時發生錯誤: {e}")
            self.clear_details()
    
    def update_details(self, text):
        """更新詳細資訊"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, text)
        self.details_text.config(state=tk.DISABLED)
    
    def clear_details(self):
        """清除詳細資訊"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state=tk.DISABLED)
    
    def show_file_details(self):
        """顯示檔案詳細資訊對話框"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        original_name = self.tree.item(item, 'text')
        
        # 尋找對應的預覽結果
        result = None
        for r in self.preview_results:
            if r['original_name'] == original_name:
                result = r
                break
        
        if result:
            from tkinter import messagebox
            
            details = f"檔案詳細資訊\n\n"
            details += f"原檔名: {result['original_name']}\n"
            details += f"新檔名: {result['new_name']}\n"
            details += f"檔案大小: {self.format_file_size(result['size'])}\n"
            details += f"修改時間: {result['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            details += f"完整路徑: {result['full_path']}\n"
            
            if result['conflict']:
                details += f"\n⚠️ 衝突原因: {result['conflict_reason']}"
            
            messagebox.showinfo("檔案詳細資訊", details)
    
    def show_in_explorer(self):
        """在檔案總管中顯示"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        original_name = self.tree.item(item, 'text')
        
        # 尋找對應的預覽結果
        result = None
        for r in self.preview_results:
            if r['original_name'] == original_name:
                result = r
                break
        
        if result:
            try:
                import subprocess
                subprocess.run(['explorer', '/select,', result['full_path']], check=True)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("錯誤", f"無法開啟檔案總管:\n{str(e)}")
    
    def exclude_file(self):
        """排除檔案（此功能需要擴展檔案過濾器）"""
        # 這個功能可以在未來版本中實現
        from tkinter import messagebox
        messagebox.showinfo("功能提示", "此功能將在未來版本中實現")
    
    def include_only_this(self):
        """僅處理此檔案（此功能需要擴展檔案過濾器）"""
        # 這個功能可以在未來版本中實現
        from tkinter import messagebox
        messagebox.showinfo("功能提示", "此功能將在未來版本中實現")