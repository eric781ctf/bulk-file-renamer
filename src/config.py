#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
應用程式設定
Application Configuration
"""

# 應用程式資訊
APP_NAME = "批量檔案重命名工具"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Bulk File Renamer Team"
APP_DESCRIPTION = "功能豐富的桌面檔案重命名工具"

# 檔案設定
SETTINGS_FILE = "settings.json"
HISTORY_FILE = "history.json"

# 預設設定
DEFAULT_SETTINGS = {
    'last_directory': '',
    'window_geometry': '1000x700',
    'recent_rules': [],
    'auto_save': True,
    'confirm_operations': True,
    'show_hidden_files': False,
    'theme': 'default'
}

# 支援的檔案類型
SUPPORTED_FILE_TYPES = [
    '.txt', '.doc', '.docx', '.pdf',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.mp3', '.mp4', '.avi', '.mov',
    '.xlsx', '.xls', '.csv',
    '.ppt', '.pptx',
    '.zip', '.rar', '.7z'
]

# Windows 系統保留檔名
WINDOWS_RESERVED_NAMES = [
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
]

# 無效檔名字元 (Windows)
INVALID_FILENAME_CHARS = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']

# 最大歷史記錄數量
MAX_HISTORY_ENTRIES = 50

# GUI 設定
GUI_SETTINGS = {
    'default_font': ('Microsoft YaHei', 9),
    'title_font': ('Microsoft YaHei', 12, 'bold'),
    'monospace_font': ('Consolas', 9),
    'colors': {
        'success': '#28a745',
        'warning': '#ffc107', 
        'error': '#dc3545',
        'info': '#17a2b8'
    }
}