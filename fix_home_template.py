#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

file_path = r'f:\Bhrikutimandap\templates\store\home.html'

try:
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Store original for comparison
    original = content
    
    # Fix all template syntax errors
    content = content.replace("sort_price=='low_to_high'", "sort_price == 'low_to_high'")
    content = content.replace("sort_price=='high_to_low'", "sort_price == 'high_to_low'")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if original != content:
        print("✓ Template fixed successfully!")
        print(f"✓ File saved to: {file_path}")
    else:
        print("⚠ No changes needed - file already correct")
        
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
