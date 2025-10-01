#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量檔案重命名工具 - 源碼模組
Bulk File Renamer - Source Module
"""

__version__ = "1.0.0"
__author__ = "Bulk File Renamer Team"

from .file_renamer import FileRenamer, RenameRule

__all__ = [
    'FileRenamer',
    'RenameRule'
]