#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
規則設定面板
Rule Configuration Panel
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.file_renamer import RenameRule

class RulePanel:
    """規則設定面板類別"""
    
    def __init__(self, parent, file_renamer):
        self.parent = parent
        self.file_renamer = file_renamer
        
        # 創建主框架
        self.frame = ttk.LabelFrame(parent, text="重命名規則設定", padding=10)
        
        self.create_widgets()
        self.current_rule = RenameRule()
    
    def create_widgets(self):
        """創建界面組件"""
        # 規則類型選擇
        rule_type_frame = ttk.Frame(self.frame)
        rule_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rule_type_frame, text="規則類型:").pack(side=tk.LEFT)
        
        self.rule_type_var = tk.StringVar(value="prefix")
        rule_type_combo = ttk.Combobox(rule_type_frame, textvariable=self.rule_type_var, 
                                     values=["prefix", "suffix", "replace", "sequence", "case"],
                                     state="readonly")
        rule_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        rule_type_combo.bind('<<ComboboxSelected>>', self.on_rule_type_changed)
        
        # 設定一個容器來容納不同規則的設定界面
        self.settings_frame = ttk.Frame(self.frame)
        self.settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 創建不同規則類型的設定界面
        self.create_prefix_suffix_settings()
        self.create_replace_settings()
        self.create_sequence_settings()
        self.create_case_settings()
        
        # 預設顯示前綴設定
        self.show_prefix_suffix_settings()
        
        # 檔案過濾設定
        filter_frame = ttk.LabelFrame(self.frame, text="檔案過濾", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="副檔名過濾\n(用逗號分隔):").pack(anchor=tk.W)
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        filter_entry.pack(fill=tk.X, pady=(5, 10))
        filter_entry.bind('<KeyRelease>', self.on_filter_changed)
        
        ttk.Label(filter_frame, text="例如: .txt,.jpg,.png").pack(anchor=tk.W)
        
        # 操作按鈕
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="應用規則", command=self.apply_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清除規則", command=self.clear_rules).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="重設", command=self.reset_form).pack(side=tk.LEFT)
        
        # 已套用規則列表
        rules_list_frame = ttk.LabelFrame(self.frame, text="已套用的規則", padding=10)
        rules_list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 建立樹狀檢視來顯示規則
        self.rules_tree = ttk.Treeview(rules_list_frame, columns=('type', 'description'), 
                                      show='tree headings', height=4)
        self.rules_tree.heading('#0', text='順序')
        self.rules_tree.heading('type', text='類型')
        self.rules_tree.heading('description', text='描述')
        
        self.rules_tree.column('#0', width=50)
        self.rules_tree.column('type', width=80)
        self.rules_tree.column('description', width=200)
        
        # 添加滾動條
        rules_scrollbar = ttk.Scrollbar(rules_list_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=rules_scrollbar.set)
        
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rules_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 規則操作按鈕
        rules_button_frame = ttk.Frame(rules_list_frame)
        rules_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(rules_button_frame, text="上移", command=self.move_rule_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rules_button_frame, text="下移", command=self.move_rule_down).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rules_button_frame, text="刪除", command=self.delete_rule).pack(side=tk.LEFT)
    
    def create_prefix_suffix_settings(self):
        """創建前綴/後綴設定界面"""
        self.prefix_suffix_frame = ttk.Frame(self.settings_frame)
        
        # 前綴設定
        prefix_frame = ttk.Frame(self.prefix_suffix_frame)
        prefix_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(prefix_frame, text="前綴:").pack(side=tk.LEFT)
        self.prefix_var = tk.StringVar()
        ttk.Entry(prefix_frame, textvariable=self.prefix_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 後綴設定
        suffix_frame = ttk.Frame(self.prefix_suffix_frame)
        suffix_frame.pack(fill=tk.X)
        
        ttk.Label(suffix_frame, text="後綴:").pack(side=tk.LEFT)
        self.suffix_var = tk.StringVar()
        ttk.Entry(suffix_frame, textvariable=self.suffix_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    def create_replace_settings(self):
        """創建替換設定界面"""
        self.replace_frame = ttk.Frame(self.settings_frame)
        
        # 尋找文字
        find_frame = ttk.Frame(self.replace_frame)
        find_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(find_frame, text="尋找:").pack(side=tk.LEFT)
        self.find_var = tk.StringVar()
        ttk.Entry(find_frame, textvariable=self.find_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 替換文字
        replace_frame = ttk.Frame(self.replace_frame)
        replace_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(replace_frame, text="替換為:").pack(side=tk.LEFT)
        self.replace_var = tk.StringVar()
        ttk.Entry(replace_frame, textvariable=self.replace_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 包含副檔名選項
        self.include_ext_var = tk.BooleanVar()
        ttk.Checkbutton(self.replace_frame, text="包含副檔名", 
                       variable=self.include_ext_var).pack(anchor=tk.W)
    
    def create_sequence_settings(self):
        """創建序列編號設定界面"""
        self.sequence_frame = ttk.Frame(self.settings_frame)
        
        # 起始編號
        start_frame = ttk.Frame(self.sequence_frame)
        start_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(start_frame, text="起始編號:").pack(side=tk.LEFT)
        self.start_var = tk.StringVar(value="1")
        start_spinbox = ttk.Spinbox(start_frame, textvariable=self.start_var, 
                                   from_=0, to=9999, width=10)
        start_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # 位數
        digits_frame = ttk.Frame(self.sequence_frame)
        digits_frame.pack(fill=tk.X)
        
        ttk.Label(digits_frame, text="位數:").pack(side=tk.LEFT)
        self.digits_var = tk.StringVar(value="3")
        digits_spinbox = ttk.Spinbox(digits_frame, textvariable=self.digits_var, 
                                    from_=1, to=10, width=10)
        digits_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(self.sequence_frame, text="例如: 001, 002, 003...").pack(anchor=tk.W, pady=(10, 0))
    
    def create_case_settings(self):
        """創建大小寫設定界面"""
        self.case_frame = ttk.Frame(self.settings_frame)
        
        ttk.Label(self.case_frame, text="大小寫轉換:").pack(anchor=tk.W, pady=(0, 10))
        
        self.case_var = tk.StringVar(value="keep")
        
        options = [
            ("保持原樣", "keep"),
            ("全部大寫", "upper"),
            ("全部小寫", "lower"),
            ("首字母大寫", "capitalize"),
            ("標題格式", "title")
        ]
        
        for text, value in options:
            ttk.Radiobutton(self.case_frame, text=text, variable=self.case_var, 
                           value=value).pack(anchor=tk.W, pady=2)
    
    def show_prefix_suffix_settings(self):
        """顯示前綴/後綴設定"""
        self.hide_all_settings()
        self.prefix_suffix_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_replace_settings(self):
        """顯示替換設定"""
        self.hide_all_settings()
        self.replace_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_sequence_settings(self):
        """顯示序列編號設定"""
        self.hide_all_settings()
        self.sequence_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_case_settings(self):
        """顯示大小寫設定"""
        self.hide_all_settings()
        self.case_frame.pack(fill=tk.BOTH, expand=True)
    
    def hide_all_settings(self):
        """隱藏所有設定界面"""
        for frame in [self.prefix_suffix_frame, self.replace_frame, 
                     self.sequence_frame, self.case_frame]:
            frame.pack_forget()
    
    def on_rule_type_changed(self, event=None):
        """規則類型改變事件"""
        rule_type = self.rule_type_var.get()
        
        if rule_type in ["prefix", "suffix"]:
            self.show_prefix_suffix_settings()
        elif rule_type == "replace":
            self.show_replace_settings()
        elif rule_type == "sequence":
            self.show_sequence_settings()
        elif rule_type == "case":
            self.show_case_settings()
    
    def on_filter_changed(self, event=None):
        """檔案過濾改變事件"""
        filter_text = self.filter_var.get().strip()
        if filter_text:
            # 分割並清理過濾條件
            filters = [f.strip() for f in filter_text.split(',') if f.strip()]
            # 確保副檔名格式正確
            filters = [f if f.startswith('.') else f'.{f}' for f in filters]
        else:
            filters = []
        
        self.file_renamer.set_file_filters(filters)
    
    def apply_rule(self):
        """應用當前規則"""
        rule_type = self.rule_type_var.get()
        rule = RenameRule()
        rule.rule_type = rule_type
        
        try:
            if rule_type == "prefix":
                prefix = self.prefix_var.get().strip()
                if not prefix:
                    messagebox.showwarning("警告", "請輸入前綴內容")
                    return
                rule.prefix = prefix
                
            elif rule_type == "suffix":
                suffix = self.suffix_var.get().strip()
                if not suffix:
                    messagebox.showwarning("警告", "請輸入後綴內容")
                    return
                rule.suffix = suffix
                
            elif rule_type == "replace":
                find_text = self.find_var.get()
                if not find_text:
                    messagebox.showwarning("警告", "請輸入要尋找的文字")
                    return
                rule.find_text = find_text
                rule.replace_text = self.replace_var.get()
                rule.include_extension = self.include_ext_var.get()
                
            elif rule_type == "sequence":
                try:
                    rule.sequence_start = int(self.start_var.get())
                    rule.sequence_digits = int(self.digits_var.get())
                except ValueError:
                    messagebox.showerror("錯誤", "請輸入有效的數字")
                    return
                    
            elif rule_type == "case":
                rule.case_option = self.case_var.get()
            
            # 添加規則
            self.file_renamer.add_rename_rule(rule)
            self.refresh_rules_list()
            
            # 清除表單
            self.reset_form()
            
        except Exception as e:
            messagebox.showerror("錯誤", f"應用規則時發生錯誤:\n{str(e)}")
    
    def clear_rules(self):
        """清除所有規則"""
        if messagebox.askyesno("確認", "確定要清除所有規則嗎？"):
            self.file_renamer.clear_rename_rules()
            self.refresh_rules_list()
    
    def reset_form(self):
        """重設表單"""
        self.prefix_var.set("")
        self.suffix_var.set("")
        self.find_var.set("")
        self.replace_var.set("")
        self.include_ext_var.set(False)
        self.start_var.set("1")
        self.digits_var.set("3")
        self.case_var.set("keep")
    
    def refresh_rules_list(self):
        """刷新規則列表"""
        # 清除現有項目
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # 添加規則
        for i, rule in enumerate(self.file_renamer.rename_rules):
            description = self.get_rule_description(rule)
            self.rules_tree.insert('', 'end', text=str(i+1), 
                                  values=(rule.rule_type, description))
    
    def get_rule_description(self, rule):
        """獲取規則描述"""
        if rule.rule_type == "prefix":
            return f"添加前綴: '{rule.prefix}'"
        elif rule.rule_type == "suffix":
            return f"添加後綴: '{rule.suffix}'"
        elif rule.rule_type == "replace":
            ext_note = " (含副檔名)" if rule.include_extension else ""
            return f"'{rule.find_text}' → '{rule.replace_text}'{ext_note}"
        elif rule.rule_type == "sequence":
            return f"序列編號: {rule.sequence_start}, {rule.sequence_digits}位數"
        elif rule.rule_type == "case":
            case_names = {
                "keep": "保持原樣",
                "upper": "全部大寫",
                "lower": "全部小寫",
                "capitalize": "首字母大寫",
                "title": "標題格式"
            }
            return f"大小寫: {case_names.get(rule.case_option, rule.case_option)}"
        return "未知規則"
    
    def move_rule_up(self):
        """上移規則"""
        selection = self.rules_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.rules_tree.index(item)
        
        if index > 0:
            # 交換規則順序
            rules = self.file_renamer.rename_rules
            rules[index], rules[index-1] = rules[index-1], rules[index]
            self.refresh_rules_list()
            
            # 重新選擇項目
            new_item = self.rules_tree.get_children()[index-1]
            self.rules_tree.selection_set(new_item)
    
    def move_rule_down(self):
        """下移規則"""
        selection = self.rules_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.rules_tree.index(item)
        rules = self.file_renamer.rename_rules
        
        if index < len(rules) - 1:
            # 交換規則順序
            rules[index], rules[index+1] = rules[index+1], rules[index]
            self.refresh_rules_list()
            
            # 重新選擇項目
            new_item = self.rules_tree.get_children()[index+1]
            self.rules_tree.selection_set(new_item)
    
    def delete_rule(self):
        """刪除規則"""
        selection = self.rules_tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("確認", "確定要刪除選中的規則嗎？"):
            item = selection[0]
            index = self.rules_tree.index(item)
            
            # 刪除規則
            del self.file_renamer.rename_rules[index]
            self.refresh_rules_list()