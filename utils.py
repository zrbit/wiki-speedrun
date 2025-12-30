import sqlite3

def get_popular_links(db_path, limit=1):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM popular_links ORDER BY RANDOM() LIMIT ?", (limit,))
    popular_links = [ row[0] for row in cursor.fetchall()]

    conn.close()
    return popular_links

def get_random_links(db_path, limit=1):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM random_links ORDER BY RANDOM() LIMIT ?", (limit,))
    random_links = [row[0] for row in cursor.fetchall()]
    conn.close()
    return random_links