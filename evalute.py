import sqlite3
import json

from traversal import naive_traversal, embedding_traversal, better_embedding_traversal


def get_popular_links(db_path, limit=200):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM popular_links ORDER BY RANDOM() LIMIT ?", (limit,))
    popular_links = [ row[0] for row in cursor.fetchall()]

    conn.close()
    return popular_links

def get_random_links(db_path, limit=200):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM random_links ORDER BY RANDOM() LIMIT ?", (limit,))
    random_links = [row[0] for row in cursor.fetchall()]
    conn.close()
    return random_links


def evaluate_traversal(traversal_func, start_links, end_links, difficulty):
    time, link, path, found = traversal_func(start_links, end_links)
    result = {
        "start_link": start_links,
        "end_link": end_links,
        "difficulty": difficulty,
        "traversal_method": traversal_func.__name__,
        "time_taken": time,
        "links_traversed": link, #convert to list
        "traversal_path": list(path),
        "found": found
    }
    return result

def run_evaluations(db_path):
    popular_links = get_popular_links(db_path)
    random_links = get_random_links(db_path)

    link_pairs = []
    for i in range(5):
        link_pairs.append((popular_links[i], popular_links[i+1], "easy"))
        link_pairs.append((popular_links[i], random_links[i], "medium"))
        link_pairs.append((random_links[i], popular_links[i], "hard"))

    traversal_methods = [naive_traversal, embedding_traversal, better_embedding_traversal]
    results = []
    for start_link, end_link, difficulty in link_pairs:
        for method in traversal_methods:
            print(f"Evaluating {method.__name__} from {start_link} to {end_link}")
            result = evaluate_traversal(method, start_link, end_link, difficulty)
            results.append(result)
    #save results to a file it's in list of dicts
    with open("evaluation_results.json", "w") as f:
        #serialize results to json
        json.dump(results, f, indent=4)
    

def main():
    db_path = "wiki_links.db"
    run_evaluations(db_path)

if __name__ == "__main__":
    main()
    

    