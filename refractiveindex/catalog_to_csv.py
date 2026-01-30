import yaml
import pandas as pd

def parse_catalog(yml_path):
    with open(yml_path, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)
    
    rows = []
    
    for shelf_item in catalog:
        shelf_id = shelf_item.get('SHELF')
        shelf_name = shelf_item.get('name')
        
        # 遍历 SHELF 下的内容 (可能是 BOOK 或 DIVIDER)
        for book_item in shelf_item.get('content', []):
            if 'BOOK' in book_item:
                book_id = book_item.get('BOOK')
                book_name = book_item.get('name')
                
                # 遍历 BOOK 下的内容 (可能是 PAGE 或 DIVIDER)
                for page_item in book_item.get('content', []):
                    if 'PAGE' in page_item:
                        page_id = page_item.get('PAGE')
                        page_display_name = page_item.get('name')
                        
                        rows.append({
                            "shelf_id": shelf_id,
                            "shelf_name": shelf_name,
                            "book_id": book_id,
                            "book_name": book_name,
                            "page_id": page_id,
                            "page_name": page_display_name
                        })
                        
    return pd.DataFrame(rows)

# 执行并保存
df = parse_catalog("refractiveindex.info-database/catalog-nk.yml")
df.to_csv("materials_index.csv", index=False)