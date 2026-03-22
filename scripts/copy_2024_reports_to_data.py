# -*- coding: utf-8 -*-
import os
import shutil

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(base_dir, 'public', 'data', 'history', '2024')
    target_dir = os.path.join(base_dir, 'public', 'data')
    
    print(f"源目录: {source_dir}")
    print(f"目标目录: {target_dir}")
    
    copied_count = 0
    for filename in sorted(os.listdir(source_dir)):
        if filename.endswith('.json'):
            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)
            
            print(f"复制: {filename}")
            shutil.copy2(source_path, target_path)
            copied_count += 1
    
    print(f"\n完成! 共复制了 {copied_count} 个文件")

if __name__ == '__main__':
    main()
