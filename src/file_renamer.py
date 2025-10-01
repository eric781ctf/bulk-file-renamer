#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案重命名核心邏輯
Core file renaming logic
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path

class RenameRule:
    """重命名規則類別"""
    
    def __init__(self):
        self.rule_type = "none"  # none, prefix, suffix, replace, sequence, case
        self.prefix = ""
        self.suffix = ""
        self.find_text = ""
        self.replace_text = ""
        self.sequence_start = 1
        self.sequence_digits = 3
        self.case_option = "keep"  # keep, upper, lower, title, capitalize
        self.include_extension = False

class FileRenamer:
    """檔案重命名器主類別"""
    
    def __init__(self):
        self.source_directory = ""
        self.files_list = []
        self.filtered_files = []
        self.rename_rules = []
        self.file_filters = []
        self.history = []
        self.settings = self.load_settings()
    
    def set_source_directory(self, directory: str) -> bool:
        """設定來源目錄"""
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return False
        
        self.source_directory = directory
        self.refresh_files_list()
        return True
    
    def refresh_files_list(self):
        """刷新檔案列表"""
        if not self.source_directory:
            return
        
        self.files_list = []
        try:
            for filename in os.listdir(self.source_directory):
                filepath = os.path.join(self.source_directory, filename)
                if os.path.isfile(filepath):
                    self.files_list.append({
                        'original_name': filename,
                        'full_path': filepath,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                    })
            
            # 按檔名排序
            self.files_list.sort(key=lambda x: x['original_name'].lower())
            self.apply_filters()
            
        except Exception as e:
            print(f"讀取檔案列表時發生錯誤: {e}")
    
    def set_file_filters(self, filters: List[str]):
        """設定檔案過濾器"""
        self.file_filters = filters
        self.apply_filters()
    
    def apply_filters(self):
        """應用檔案過濾器"""
        if not self.file_filters:
            self.filtered_files = self.files_list.copy()
            return
        
        self.filtered_files = []
        for file_info in self.files_list:
            filename = file_info['original_name']
            file_ext = os.path.splitext(filename)[1].lower()
            
            # 檢查是否符合任一過濾條件
            for filter_pattern in self.file_filters:
                if filter_pattern.startswith('.'):
                    # 副檔名過濾
                    if file_ext == filter_pattern.lower():
                        self.filtered_files.append(file_info)
                        break
                else:
                    # 檔名模式過濾
                    if re.search(filter_pattern, filename, re.IGNORECASE):
                        self.filtered_files.append(file_info)
                        break
    
    def add_rename_rule(self, rule: RenameRule):
        """添加重命名規則"""
        self.rename_rules.append(rule)
    
    def clear_rename_rules(self):
        """清除所有重命名規則"""
        self.rename_rules.clear()
    
    def preview_rename(self) -> List[Dict]:
        """預覽重命名結果"""
        preview_results = []
        
        for i, file_info in enumerate(self.filtered_files):
            original_name = file_info['original_name']
            new_name = self.apply_rename_rules(original_name, i)
            
            # 檢查衝突
            conflict = False
            conflict_reason = ""
            
            # 檢查檔名是否有效
            if not self.is_valid_filename(new_name):
                conflict = True
                conflict_reason = "檔名包含無效字元"
            
            # 檢查是否與現有檔案衝突
            new_path = os.path.join(self.source_directory, new_name)
            if os.path.exists(new_path) and new_name != original_name:
                conflict = True
                conflict_reason = "檔名已存在"
            
            preview_results.append({
                'original_name': original_name,
                'new_name': new_name,
                'full_path': file_info['full_path'],
                'conflict': conflict,
                'conflict_reason': conflict_reason,
                'size': file_info['size'],
                'modified': file_info['modified']
            })
        
        return preview_results
    
    def apply_rename_rules(self, filename: str, index: int) -> str:
        """應用重命名規則到單個檔名"""
        name, ext = os.path.splitext(filename)
        result_name = name
        
        for rule in self.rename_rules:
            if rule.rule_type == "prefix":
                result_name = rule.prefix + result_name
            
            elif rule.rule_type == "suffix":
                result_name = result_name + rule.suffix
            
            elif rule.rule_type == "replace":
                if rule.include_extension:
                    full_name = result_name + ext
                    full_name = full_name.replace(rule.find_text, rule.replace_text)
                    result_name, ext = os.path.splitext(full_name)
                else:
                    result_name = result_name.replace(rule.find_text, rule.replace_text)
            
            elif rule.rule_type == "sequence":
                sequence_num = str(rule.sequence_start + index).zfill(rule.sequence_digits)
                result_name = sequence_num
            
            elif rule.rule_type == "case":
                if rule.case_option == "upper":
                    result_name = result_name.upper()
                elif rule.case_option == "lower":
                    result_name = result_name.lower()
                elif rule.case_option == "title":
                    result_name = result_name.title()
                elif rule.case_option == "capitalize":
                    result_name = result_name.capitalize()
        
        return result_name + ext
    
    def execute_rename(self, preview_results: List[Dict]) -> Tuple[int, int, List[str]]:
        """執行重命名操作"""
        success_count = 0
        error_count = 0
        errors = []
        rename_operations = []
        
        try:
            for result in preview_results:
                if result['conflict']:
                    error_count += 1
                    errors.append(f"{result['original_name']}: {result['conflict_reason']}")
                    continue
                
                if result['original_name'] == result['new_name']:
                    continue  # 檔名沒有變化，跳過
                
                old_path = result['full_path']
                new_path = os.path.join(self.source_directory, result['new_name'])
                
                try:
                    os.rename(old_path, new_path)
                    success_count += 1
                    rename_operations.append({
                        'old_name': result['original_name'],
                        'new_name': result['new_name'],
                        'old_path': old_path,
                        'new_path': new_path,
                        'timestamp': datetime.now()
                    })
                except Exception as e:
                    error_count += 1
                    errors.append(f"{result['original_name']}: {str(e)}")
            
            # 記錄操作歷史
            if rename_operations:
                self.history.append({
                    'timestamp': datetime.now(),
                    'operations': rename_operations,
                    'directory': self.source_directory
                })
                self.save_history()
            
            # 刷新檔案列表
            self.refresh_files_list()
            
        except Exception as e:
            errors.append(f"執行重命名時發生錯誤: {str(e)}")
            error_count += 1
        
        return success_count, error_count, errors
    
    def undo_last_operation(self) -> bool:
        """復原上一次操作"""
        if not self.history:
            return False
        
        try:
            last_operation = self.history[-1]
            operations = last_operation['operations']
            
            # 反向執行操作
            for op in reversed(operations):
                if os.path.exists(op['new_path']):
                    os.rename(op['new_path'], op['old_path'])
            
            # 從歷史記錄中移除
            self.history.pop()
            self.save_history()
            
            # 刷新檔案列表
            self.refresh_files_list()
            
            return True
            
        except Exception as e:
            print(f"復原操作時發生錯誤: {e}")
            return False
    
    def is_valid_filename(self, filename: str) -> bool:
        """檢查檔名是否有效"""
        if not filename or filename in ['', '.', '..']:
            return False
        
        # Windows 無效字元
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in filename:
                return False
        
        # Windows 保留名稱
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                         'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 
                         'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 
                         'LPT7', 'LPT8', 'LPT9']
        
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    def load_settings(self) -> Dict:
        """載入設定"""
        settings_file = "settings.json"
        default_settings = {
            'last_directory': '',
            'window_geometry': '800x600',
            'recent_rules': []
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"載入設定時發生錯誤: {e}")
        
        return default_settings
    
    def save_settings(self, settings: Dict):
        """儲存設定"""
        try:
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定時發生錯誤: {e}")
    
    def save_history(self):
        """儲存操作歷史"""
        try:
            # 只保留最近20次操作
            history_to_save = self.history[-20:] if len(self.history) > 20 else self.history
            
            # 轉換datetime為字串以便JSON序列化
            serializable_history = []
            for entry in history_to_save:
                serializable_entry = {
                    'timestamp': entry['timestamp'].isoformat(),
                    'directory': entry['directory'],
                    'operations': []
                }
                
                for op in entry['operations']:
                    serializable_op = {
                        'old_name': op['old_name'],
                        'new_name': op['new_name'],
                        'old_path': op['old_path'],
                        'new_path': op['new_path'],
                        'timestamp': op['timestamp'].isoformat()
                    }
                    serializable_entry['operations'].append(serializable_op)
                
                serializable_history.append(serializable_entry)
            
            with open("history.json", 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"儲存歷史記錄時發生錯誤: {e}")
    
    def load_history(self):
        """載入操作歷史"""
        try:
            if os.path.exists("history.json"):
                with open("history.json", 'r', encoding='utf-8') as f:
                    serializable_history = json.load(f)
                
                # 轉換字串回datetime
                self.history = []
                for entry in serializable_history:
                    history_entry = {
                        'timestamp': datetime.fromisoformat(entry['timestamp']),
                        'directory': entry['directory'],
                        'operations': []
                    }
                    
                    for op in entry['operations']:
                        operation = {
                            'old_name': op['old_name'],
                            'new_name': op['new_name'],
                            'old_path': op['old_path'],
                            'new_path': op['new_path'],
                            'timestamp': datetime.fromisoformat(op['timestamp'])
                        }
                        history_entry['operations'].append(operation)
                    
                    self.history.append(history_entry)
                    
        except Exception as e:
            print(f"載入歷史記錄時發生錯誤: {e}")
            self.history = []