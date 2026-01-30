import sqlite3
import yaml

def build_sqlite_db(yml_path, db_path="materials.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 创建表结构
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS shelves (
            id TEXT PRIMARY KEY,
            name TEXT
        );
        CREATE TABLE IF NOT EXISTS books (
            id TEXT,
            shelf_id TEXT,
            name TEXT,
            PRIMARY KEY (id, shelf_id),
            FOREIGN KEY (shelf_id) REFERENCES shelves (id)
        );
        CREATE TABLE IF NOT EXISTS pages (
            id TEXT,
            book_id TEXT,
            shelf_id TEXT,
            name TEXT,
            PRIMARY KEY (id, book_id, shelf_id),
            FOREIGN KEY (book_id, shelf_id) REFERENCES books (id, shelf_id)
        );
    ''')

    with open(yml_path, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    for s_item in catalog:
        s_id, s_name = s_item.get('SHELF'), s_item.get('name')
        if not s_id: continue
        cursor.execute("INSERT OR REPLACE INTO shelves VALUES (?, ?)", (s_id, s_name))

        for b_item in s_item.get('content', []):
            if 'BOOK' in b_item:
                b_id, b_name = b_item.get('BOOK'), b_item.get('name')
                cursor.execute("INSERT OR REPLACE INTO books VALUES (?, ?, ?)", (b_id, s_id, b_name))

                for p_item in b_item.get('content', []):
                    if 'PAGE' in p_item:
                        p_id, p_name = p_item.get('PAGE'), p_item.get('name')
                        cursor.execute("INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?)", 
                                       (p_id, b_id, s_id, p_name))
    
    conn.commit()
    conn.close()
    print(f"数据库 {db_path} 构建成功！")

# 执行转换
build_sqlite_db("refractiveindex.info-database/catalog-nk.yml")