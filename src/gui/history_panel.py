#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歷史記錄面板
History Panel
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime

class HistoryPanel:
    """歷史記錄面板類別"""
    
    def __init__(self, parent, file_renamer):
        self.parent = parent
        self.file_renamer = file_renamer
        
        self.create_widgets()
    
    def create_widgets(self):
        """創建界面組件"""
        # 創建主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 工具欄
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="刷新歷史", command=self.refresh_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="清除歷史", command=self.clear_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="匯出歷史", command=self.export_history).pack(side=tk.LEFT, padx=(0, 5))
        
        # 統計資訊
        self.stats_var = tk.StringVar()
        stats_label = ttk.Label(toolbar_frame, textvariable=self.stats_var)
        stats_label.pack(side=tk.RIGHT)
        
        # 創建分割窗格
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 上半部：歷史記錄列表
        history_frame = ttk.LabelFrame(paned_window, text="操作歷史", padding=10)
        paned_window.add(history_frame, weight=1)
        
        # 歷史記錄樹狀檢視
        columns = ('files_count', 'directory', 'timestamp')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='tree headings')
        
        self.history_tree.heading('#0', text='操作編號')
        self.history_tree.heading('files_count', text='檔案數量')
        self.history_tree.heading('directory', text='目錄')
        self.history_tree.heading('timestamp', text='執行時間')
        
        self.history_tree.column('#0', width=80)
        self.history_tree.column('files_count', width=80)
        self.history_tree.column('directory', width=300)
        self.history_tree.column('timestamp', width=150)
        
        # 滾動條
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下半部：操作詳細資訊
        details_frame = ttk.LabelFrame(paned_window, text="操作詳細資訊", padding=10)
        paned_window.add(details_frame, weight=1)
        
        # 詳細資訊樹狀檢視
        detail_columns = ('new_name', 'operation_time')
        self.details_tree = ttk.Treeview(details_frame, columns=detail_columns, show='tree headings')
        
        self.details_tree.heading('#0', text='原檔名')
        self.details_tree.heading('new_name', text='新檔名')
        self.details_tree.heading('operation_time', text='操作時間')
        
        self.details_tree.column('#0', width=200)
        self.details_tree.column('new_name', width=200)
        self.details_tree.column('operation_time', width=150)
        
        # 滾動條
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_tree.yview)
        self.details_tree.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 操作按鈕框架
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="復原此操作", command=self.undo_selected_operation).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="刪除此記錄", command=self.delete_selected_record).pack(side=tk.LEFT, padx=(0, 5))
        
        # 綁定事件
        self.history_tree.bind('<<TreeviewSelect>>', self.on_history_selection_changed)
        self.history_tree.bind('<Double-1>', self.on_history_double_click)
        
        # 初始化載入歷史
        self.refresh_history()
    
    def refresh_history(self):
        """刷新歷史記錄"""
        # 清除現有項目
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
        
        # 載入歷史記錄
        history = self.file_renamer.history
        
        if not history:
            self.update_stats(0, 0)
            return
        
        total_operations = len(history)
        total_files = sum(len(entry['operations']) for entry in history)
        
        # 按時間倒序顯示（最新的在上面）
        for i, entry in enumerate(reversed(history)):
            operation_id = total_operations - i
            files_count = len(entry['operations'])
            directory = entry['directory']
            timestamp = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            # 插入歷史記錄項目
            item = self.history_tree.insert('', 'end', text=f"#{operation_id}",
                                          values=(files_count, directory, timestamp))
            
            # 儲存索引以便後續使用
            self.history_tree.set(item, 'history_index', len(history) - 1 - i)
        
        self.update_stats(total_operations, total_files)
    
    def update_stats(self, operations, files):
        """更新統計資訊"""
        self.stats_var.set(f"總操作數: {operations} | 總檔案數: {files}")
    
    def on_history_selection_changed(self, event):
        """歷史記錄選擇改變事件"""
        selection = self.history_tree.selection()
        if not selection:
            self.clear_details()
            return
        
        item = selection[0]
        try:
            history_index = int(self.history_tree.set(item, 'history_index'))
            self.show_operation_details(history_index)
        except (ValueError, IndexError):
            self.clear_details()
    
    def on_history_double_click(self, event):
        """歷史記錄雙擊事件"""
        item = self.history_tree.identify('item', event.x, event.y)
        if item:
            self.show_operation_info()
    
    def show_operation_details(self, history_index):
        """顯示操作詳細資訊"""
        # 清除現有詳細資訊
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
        
        try:
            history_entry = self.file_renamer.history[history_index]
            operations = history_entry['operations']
            
            # 顯示每個檔案的重命名操作
            for operation in operations:
                old_name = operation['old_name']
                new_name = operation['new_name']
                op_time = operation['timestamp'].strftime("%H:%M:%S")
                
                self.details_tree.insert('', 'end', text=old_name,
                                        values=(new_name, op_time))
        
        except (IndexError, KeyError) as e:
            print(f"顯示操作詳細資訊時發生錯誤: {e}")
    
    def clear_details(self):
        """清除詳細資訊"""
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
    
    def undo_selected_operation(self):
        """復原選中的操作"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "請先選擇要復原的操作")
            return
        
        item = selection[0]
        try:
            history_index = int(self.history_tree.set(item, 'history_index'))
            history_entry = self.file_renamer.history[history_index]
            
            operation_count = len(history_entry['operations'])
            operation_time = history_entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            # 檢查是否為最後一次操作
            if history_index != len(self.file_renamer.history) - 1:
                if not messagebox.askyesno("警告", 
                                         "您選擇的不是最後一次操作。\n"
                                         "復原此操作可能會導致檔案狀態不一致。\n"
                                         "建議您按順序復原最近的操作。\n\n"
                                         "是否仍要繼續？"):
                    return
            
            if not messagebox.askyesno("確認復原", 
                                     f"即將復原以下操作：\n"
                                     f"時間: {operation_time}\n"
                                     f"檔案數量: {operation_count}\n"
                                     f"目錄: {history_entry['directory']}\n\n"
                                     f"是否確定復原？"):
                return
            
            # 如果不是最後一次操作，需要特殊處理
            if history_index == len(self.file_renamer.history) - 1:
                # 最後一次操作，使用標準復原方法
                if self.file_renamer.undo_last_operation():
                    messagebox.showinfo("完成", f"成功復原 {operation_count} 個檔案的重命名")
                    self.refresh_history()
                else:
                    messagebox.showerror("錯誤", "復原操作失敗")
            else:
                # 不是最後一次操作，手動復原
                if self.manual_undo_operation(history_index):
                    messagebox.showinfo("完成", f"成功復原 {operation_count} 個檔案的重命名")
                    self.refresh_history()
                else:
                    messagebox.showerror("錯誤", "復原操作失敗")
                    
        except (ValueError, IndexError, KeyError) as e:
            messagebox.showerror("錯誤", f"復原操作時發生錯誤:\n{str(e)}")
    
    def manual_undo_operation(self, history_index):
        """手動復原指定的操作"""
        try:
            history_entry = self.file_renamer.history[history_index]
            operations = history_entry['operations']
            
            # 檢查檔案是否還存在且可以復原
            failed_operations = []
            for operation in operations:
                new_path = operation['new_path']
                old_path = operation['old_path']
                
                if not os.path.exists(new_path):
                    failed_operations.append(f"檔案不存在: {operation['new_name']}")
                elif os.path.exists(old_path):
                    failed_operations.append(f"目標檔案已存在: {operation['old_name']}")
            
            if failed_operations:
                messagebox.showerror("無法復原", 
                                   f"以下檔案無法復原:\n" + "\n".join(failed_operations))
                return False
            
            # 執行復原
            import os
            for operation in reversed(operations):
                os.rename(operation['new_path'], operation['old_path'])
            
            # 從歷史記錄中移除
            del self.file_renamer.history[history_index]
            self.file_renamer.save_history()
            
            return True
            
        except Exception as e:
            print(f"手動復原操作時發生錯誤: {e}")
            return False
    
    def delete_selected_record(self):
        """刪除選中的歷史記錄"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "請先選擇要刪除的記錄")
            return
        
        if not messagebox.askyesno("確認刪除", "確定要刪除選中的歷史記錄嗎？\n此操作無法復原。"):
            return
        
        item = selection[0]
        try:
            history_index = int(self.history_tree.set(item, 'history_index'))
            
            # 刪除歷史記錄
            del self.file_renamer.history[history_index]
            self.file_renamer.save_history()
            
            # 刷新顯示
            self.refresh_history()
            
            messagebox.showinfo("完成", "歷史記錄已刪除")
            
        except (ValueError, IndexError) as e:
            messagebox.showerror("錯誤", f"刪除歷史記錄時發生錯誤:\n{str(e)}")
    
    def clear_history(self):
        """清除所有歷史記錄"""
        if not self.file_renamer.history:
            messagebox.showinfo("資訊", "沒有歷史記錄需要清除")
            return
        
        if not messagebox.askyesno("確認清除", 
                                 f"確定要清除所有 {len(self.file_renamer.history)} 條歷史記錄嗎？\n"
                                 f"此操作無法復原。"):
            return
        
        try:
            self.file_renamer.history.clear()
            self.file_renamer.save_history()
            self.refresh_history()
            
            messagebox.showinfo("完成", "所有歷史記錄已清除")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"清除歷史記錄時發生錯誤:\n{str(e)}")
    
    def export_history(self):
        """匯出歷史記錄"""
        if not self.file_renamer.history:
            messagebox.showinfo("資訊", "沒有歷史記錄可以匯出")
            return
        
        from tkinter import filedialog
        import json
        
        try:
            filename = filedialog.asksaveasfilename(
                title="匯出歷史記錄",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                # 準備匯出資料
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'total_operations': len(self.file_renamer.history),
                    'history': []
                }
                
                for entry in self.file_renamer.history:
                    export_entry = {
                        'timestamp': entry['timestamp'].isoformat(),
                        'directory': entry['directory'],
                        'operations': []
                    }
                    
                    for op in entry['operations']:
                        export_op = {
                            'old_name': op['old_name'],
                            'new_name': op['new_name'],
                            'old_path': op['old_path'],
                            'new_path': op['new_path'],
                            'timestamp': op['timestamp'].isoformat()
                        }
                        export_entry['operations'].append(export_op)
                    
                    export_data['history'].append(export_entry)
                
                # 寫入檔案
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("完成", f"歷史記錄已匯出到:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("錯誤", f"匯出歷史記錄時發生錯誤:\n{str(e)}")
    
    def show_operation_info(self):
        """顯示操作資訊對話框"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        try:
            history_index = int(self.history_tree.set(item, 'history_index'))
            history_entry = self.file_renamer.history[history_index]
            
            info = f"操作詳細資訊\n\n"
            info += f"執行時間: {history_entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            info += f"目錄: {history_entry['directory']}\n"
            info += f"檔案數量: {len(history_entry['operations'])}\n\n"
            info += "檔案清單:\n"
            
            for i, op in enumerate(history_entry['operations'][:10]):  # 只顯示前10個
                info += f"{i+1}. {op['old_name']} → {op['new_name']}\n"
            
            if len(history_entry['operations']) > 10:
                info += f"... 以及其他 {len(history_entry['operations']) - 10} 個檔案"
            
            messagebox.showinfo("操作詳細資訊", info)
            
        except (ValueError, IndexError, KeyError) as e:
            messagebox.showerror("錯誤", f"顯示操作資訊時發生錯誤:\n{str(e)}")