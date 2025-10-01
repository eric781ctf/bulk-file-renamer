#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函數
Utility Functions
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Optional

def is_valid_filename(filename: str) -> bool:
    """
    檢查檔名是否有效
    
    Args:
        filename: 檔案名稱
        
    Returns:
        bool: 檔名是否有效
    """
    from .config import WINDOWS_RESERVED_NAMES, INVALID_FILENAME_CHARS
    
    if not filename or filename in ['', '.', '..']:
        return False
    
    # 檢查無效字元
    for char in INVALID_FILENAME_CHARS:
        if char in filename:
            return False
    
    # 檢查保留名稱
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in WINDOWS_RESERVED_NAMES:
        return False
    
    # 檢查長度（Windows 限制）
    if len(filename) > 255:
        return False
    
    return True

def format_file_size(size_bytes: int) -> str:
    """
    格式化檔案大小
    
    Args:
        size_bytes: 檔案大小（位元組）
        
    Returns:
        str: 格式化後的檔案大小
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    i = 0
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    if i == 0:
        return f"{int(size)} {size_names[i]}"
    else:
        return f"{size:.1f} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """
    清理檔名，移除或替換無效字元
    
    Args:
        filename: 原始檔名
        
    Returns:
        str: 清理後的檔名
    """
    from .config import INVALID_FILENAME_CHARS
    
    # 替換無效字元
    for char in INVALID_FILENAME_CHARS:
        filename = filename.replace(char, '_')
    
    # 移除前後空白
    filename = filename.strip()
    
    # 確保不是保留名稱
    name, ext = os.path.splitext(filename)
    from .config import WINDOWS_RESERVED_NAMES
    if name.upper() in WINDOWS_RESERVED_NAMES:
        filename = f"_{filename}"
    
    return filename

def parse_file_filters(filter_string: str) -> List[str]:
    """
    解析檔案過濾字串
    
    Args:
        filter_string: 過濾字串，如 ".txt,.jpg,.png"
        
    Returns:
        List[str]: 過濾條件列表
    """
    if not filter_string:
        return []
    
    filters = []
    for part in filter_string.split(','):
        part = part.strip()
        if part:
            if not part.startswith('.'):
                part = f'.{part}'
            filters.append(part.lower())
    
    return filters

def backup_file(filepath: str, backup_dir: str = None) -> Optional[str]:
    """
    備份檔案
    
    Args:
        filepath: 要備份的檔案路徑
        backup_dir: 備份目錄，如果為 None 則在同目錄下創建備份
        
    Returns:
        Optional[str]: 備份檔案路徑，失敗時返回 None
    """
    try:
        if not os.path.exists(filepath):
            return None
        
        # 確定備份路徑
        if backup_dir is None:
            backup_dir = os.path.dirname(filepath)
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成備份檔名
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 複製檔案
        import shutil
        shutil.copy2(filepath, backup_path)
        
        return backup_path
        
    except Exception as e:
        print(f"備份檔案時發生錯誤: {e}")
        return None

def load_json_file(filepath: str, default: Dict = None) -> Dict:
    """
    載入 JSON 檔案
    
    Args:
        filepath: JSON 檔案路徑
        default: 預設值
        
    Returns:
        Dict: JSON 資料
    """
    if default is None:
        default = {}
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"載入 JSON 檔案時發生錯誤: {e}")
    
    return default

def save_json_file(filepath: str, data: Dict) -> bool:
    """
    儲存 JSON 檔案
    
    Args:
        filepath: JSON 檔案路徑
        data: 要儲存的資料
        
    Returns:
        bool: 是否成功
    """
    try:
        # 確保目錄存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
        
    except Exception as e:
        print(f"儲存 JSON 檔案時發生錯誤: {e}")
        return False

def validate_regex(pattern: str) -> bool:
    """
    驗證正規表達式是否有效
    
    Args:
        pattern: 正規表達式模式
        
    Returns:
        bool: 是否有效
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

def get_file_info(filepath: str) -> Optional[Dict]:
    """
    獲取檔案資訊
    
    Args:
        filepath: 檔案路徑
        
    Returns:
        Optional[Dict]: 檔案資訊字典
    """
    try:
        if not os.path.exists(filepath):
            return None
        
        stat = os.stat(filepath)
        
        return {
            'name': os.path.basename(filepath),
            'path': filepath,
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'extension': os.path.splitext(filepath)[1].lower(),
            'is_file': os.path.isfile(filepath),
            'is_dir': os.path.isdir(filepath)
        }
        
    except Exception as e:
        print(f"獲取檔案資訊時發生錯誤: {e}")
        return None

def create_unique_filename(filepath: str) -> str:
    """
    創建唯一檔名（如果檔案已存在）
    
    Args:
        filepath: 原始檔案路徑
        
    Returns:
        str: 唯一檔案路徑
    """
    if not os.path.exists(filepath):
        return filepath
    
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_filepath = os.path.join(directory, new_filename)
        
        if not os.path.exists(new_filepath):
            return new_filepath
        
        counter += 1
        
        # 防止無限迴圈
        if counter > 9999:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{name}_{timestamp}{ext}"
            return os.path.join(directory, new_filename)

def log_operation(message: str, level: str = "INFO"):
    """
    記錄操作日誌
    
    Args:
        message: 日誌訊息
        level: 日誌等級 (DEBUG, INFO, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def get_available_filename(directory: str, base_name: str, extension: str) -> str:
    """
    在指定目錄中獲取可用的檔名
    
    Args:
        directory: 目錄路徑
        base_name: 基本檔名
        extension: 副檔名
        
    Returns:
        str: 可用的完整檔案路徑
    """
    filename = f"{base_name}{extension}"
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        return filepath
    
    counter = 1
    while True:
        filename = f"{base_name}_{counter}{extension}"
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            return filepath
        
        counter += 1
        
        if counter > 9999:
            break
    
    # 使用時間戳作為後備方案
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}{extension}"
    return os.path.join(directory, filename)