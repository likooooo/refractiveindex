
from typing import List, Dict, Any, Optional
from download_material import db_path
import argparse
import yaml
import re
import os

def extract_year(name_string: str) -> int:
    """
    从 PAGE 的 'name' 字段中提取四位数的年份。
    """
    match = re.search(r'(\d{4})', name_string)
    if match:
        return int(match.group(1))
    return 1000 # 如果找不到年份，返回一个极小值确保它排在最后

def get_sorted_pages_for_book(book_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    接收一个 BOOK 的 content 列表，将 PAGE 条目提取出来并按年份排序，
    然后将排序后的 PAGE 重新插入回原始的 DIVIDER 和其他非 PAGE 条目中。

    :param book_content: BOOK 字典下的 'content' 列表。
    :return: 排序后的新 content 列表。
    """
    # 1. 分离 PAGE 条目和非 PAGE 条目 (如 DIVIDER)
    page_entries = []
    other_entries = [] # 存储 DIVIDER 等，以保留其在列表中的相对位置
    
    # 使用一个字典来存储非 PAGE 条目的原始位置 (索引)
    page_start_index = -1 
    
    for i, item in enumerate(book_content):
        if 'PAGE' in item:
            page_entries.append(item)
            if page_start_index == -1:
                page_start_index = i
        else:
            other_entries.append((i, item)) # 存储索引和内容
            if page_start_index == -1:
                # 如果 PAGE 还没开始，这些非 PAGE 条目排在最前面
                pass 

    # 如果没有 PAGE 条目，直接返回原始列表
    if not page_entries:
        return book_content

    # 2. 对 PAGE 条目进行排序
    # key: extract_year, reverse=True (从新到旧)
    sorted_pages = sorted(page_entries, key=lambda p: extract_year(p.get('name', '')), reverse=True)
    
    # 3. 重建 content 列表
    
    # 在这个特定的目录结构中，DIVIDER 主要用来分隔 PAGE，
    # 它们通常位于 BOOK/content 或 PAGE 列表的开头。
    
    # 简化重建逻辑：我们只替换原始列表中所有的 PAGE 条目，保留 DIVIDER
    new_content = []
    
    # 遍历原始内容，遇到 PAGE 区域则替换
    page_index = 0
    
    for item in book_content:
        if 'PAGE' in item:
            # 遇到 PAGE，从排序好的列表中取出一个替换
            if page_index < len(sorted_pages):
                new_content.append(sorted_pages[page_index])
                page_index += 1
            # 理论上不会发生，但以防万一
            # else: continue 
        else:
            # 遇到非 PAGE 条目（如 DIVIDER），原样保留
            new_content.append(item)
            
    # 最终检查：由于我们是替换，条目总数应该不变
    if len(new_content) != len(book_content):
        warnings.warn("Error in content reconstruction: Length mismatch.")

    return new_content


def resorter_yaml_file(input_filepath: str, output_filepath: str):
    """
    读取 YAML 文件，对其中的所有 BOOK 下的 PAGE 条目按年份排序，
    然后将新的结构写回到指定的输出文件。
    """
    
    # 1. 读取并解析 YAML 文件
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The input file path was not found: {input_filepath}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

    # 2. 遍历并修改数据结构
    # data 是一个列表，包含 SHELF 字典
    
    for shelf_data in data:
        # 遍历 SHELF 内部的 content
        new_shelf_content = []
        for book_or_divider in shelf_data.get('content', []):
            
            # 检查是否为 BOOK
            if 'BOOK' in book_or_divider:
                # 找到了 BOOK，对其 content 进行排序
                book_content = book_or_divider.get('content', [])
                
                # 获取排序后的 content 列表
                sorted_book_content = get_sorted_pages_for_book(book_content)
                
                # 创建一个新的 BOOK 字典，替换旧的 content
                new_book_data = book_or_divider.copy()
                new_book_data['content'] = sorted_book_content
                new_shelf_content.append(new_book_data)
            else:
                # DIVIDER 或其他非 BOOK 条目，原样保留
                new_shelf_content.append(book_or_divider)
        
        # 替换 SHELF 的 content
        shelf_data['content'] = new_shelf_content
        
    # 3. 将修改后的数据写回新的 YAML 文件
    try:
        # 使用 Dumper 来控制输出格式。default_flow_style=False 确保输出是多行块样式，与原始文件类似。
        with open(output_filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
    except Exception as e:
        raise IOError(f"Error writing to output file {output_filepath}: {e}")
    
    print(f"\n✅ YAML catalog successfully resorted and saved to: {output_filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Reads a refractive index YAML catalog, sorts PAGE entries by publication year (Newest to Oldest), and saves the result to a new file."
    )
    parser.add_argument(
        "input_file", 
        type=str,
        nargs='?',
        default= os.path.join(db_path, "catalog-nk.yml"), 
        help="Path to the source YAML catalog file (e.g., 'catalog.yml')."
    )
    parser.add_argument(
        "output_file",
        type=str,
        nargs='?',
        default= "", 
        help="Path for the new, sorted YAML catalog file (e.g., 'sorted_catalog.yml')."
    )
    args = parser.parse_args()
    
    try:
        output_file = args.output_file if "" != args.output_file else args.input_file + ".sorted"
        resorter_yaml_file(args.input_file, output_file)
            
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"\n--- FATAL ERROR ---\n{e}")

if __name__ == "__main__":
    main()