# -*- coding: utf-8 -*-
"""
JSON转规范问答TXT转换脚本
将psy_dataset下的JSON文件转换为心理咨询问答TXT格式
"""

import json
import os
from pathlib import Path


def convert_json_to_txt(json_file_path: str, output_txt_path: str) -> bool:
    """
    将JSON文件转换为TXT问答格式
    
    Args:
        json_file_path: JSON文件路径
        output_txt_path: 输出TXT文件路径
    
    Returns:
        bool: 转换是否成功
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"错误: {json_file_path} 不是有效的JSON数组格式")
            return False
        
        qa_pairs = []
        
        for sample in data:
            messages = sample.get('messages', [])
            if not messages:
                continue
            
            for msg in messages:
                role = msg.get('role', '')
                content = msg.get('content', '').strip()
                
                if role == 'user' and content:
                    qa_pairs.append(f"Q: {content}")
                elif role == 'assistant' and content:
                    if qa_pairs:
                        qa_pairs[-1] += f"\nA: {content}"
        
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(qa_pairs))
        
        print(f"成功: {json_file_path} -> {output_txt_path}")
        print(f"转换问答对数: {len([p for p in qa_pairs if p.startswith('Q:')])}")
        return True
        
    except Exception as e:
        print(f"错误: 转换失败 - {str(e)}")
        return False


def main():
    """
    主函数：转换所有JSON文件
    """
    script_dir = Path(__file__).parent
    data_dir = script_dir / 'data' / 'psy_dataset'
    
    json_files = [
        'PsyDTCorpus_test_single_turn_split.json',
        'PsyDTCorpus_train_mulit_turn_packing.json'
    ]
    
    total_success = 0
    total_failed = 0
    
    for json_file in json_files:
        json_path = data_dir / json_file
        
        if not json_path.exists():
            print(f"跳过: {json_file} 不存在")
            total_failed += 1
            continue
        
        output_file = json_file.replace('.json', '_converted.txt')
        output_path = data_dir / output_file
        
        print(f"\n{'='*60}")
        print(f"处理文件: {json_file}")
        print(f"文件路径: {json_path}")
        print(f"输出路径: {output_path}")
        
        if convert_json_to_txt(str(json_path), str(output_path)):
            total_success += 1
        else:
            total_failed += 1
    
    print(f"\n{'='*60}")
    print(f"转换完成: 成功{total_success}个, 失败{total_failed}个")
    
    if total_success > 0:
        print(f"\n输出文件位置: {data_dir}")
        print("请检查生成的 *_converted.txt 文件")


if __name__ == '__main__':
    main()
