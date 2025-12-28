from bs4 import BeautifulSoup
import requests
import sqlite3
import random
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
import time

BASE_URL = 'https://en.wikipedia.org'
session = requests.Session()
session.headers.update({
    "User-Agent": "WikiSpeedrun/1.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})



def get_html_content(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error has occured {e}")
        return None


def get_links_and_titles(soup):
    all_links_element = soup.find_all("a")
    links = []
    titles = []
    for a in all_links_element:
        if a.has_attr("href") and a['href'].startswith("/wiki/") and not a['href'].startswith("/wiki/Special:") and not a['href'].startswith("/wiki/Help:") and not a['href'].startswith("/wiki/Wikipedia:") and not a['href'].startswith("/wiki/Category:") and not a['href'].startswith("/wiki/File:") and not a['href'].startswith("/wiki/Template:") and not a['href'].startswith("/wiki/Portal:"):
            links.append(BASE_URL + a["href"])
            titles.append(a.get("title", "No title"))
    return titles, links

def naive_traversal(start_url, end_url):
    start_time = time.time()
    html = get_html_content(start_url)
    
    link_count = 0
    traversal_path = []

    while True:
        if html:
            soup = BeautifulSoup(html, "html.parser")
            titles, links = get_links_and_titles(soup)
            if end_url in links:
                print("Found the target article!")
                break
            else:
                if not links:
                    print("No more links to follow, stopping the traversal.")
                    break
                rand_index = random.randint(0, len(links)-1)
                next_link = links[rand_index]
                traversal_path.append((titles[rand_index], next_link))
                html = get_html_content(next_link)
                link_count += 1
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    print(f"Total links traversed: {link_count}")
    print("Traversal Path:")
    for step, (title, link) in enumerate(traversal_path):
        print(f"Step {step+1}: {title} - {link}")

def embedding_traversal(start_url, end_url):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    start_time = time.time()
    html = get_html_content(start_url)
    
    link_count = 0
    traversal_path = []
    end_title = end_url.split("/wiki/")[-1].replace("_", " ")
    end_embed = model.encode([end_title], convert_to_numpy=True)[0]
    while True:
        if html:
            soup = BeautifulSoup(html, "html.parser")
            titles, links = get_links_and_titles(soup)
            if end_url in links:
                print("Found the target article!")
                break
            else:
                if not links:
                    print("No more links to follow, stopping the traversal.")
                    break
                embeds = model.encode(titles, convert_to_numpy=True)                
                #compute cosine similarity
                cosine_similarities = [dot(embed, end_embed)/(norm(embed)*norm(end_embed)) for embed in embeds]
                max_index = cosine_similarities.index(max(cosine_similarities))
                next_link = links[max_index]
                traversal_path.append((titles[max_index], next_link))
                html = get_html_content(next_link)
                link_count += 1
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    print(f"Total links traversed: {link_count}")
    print("Traversal Path:")
    for step, (title, link) in enumerate(traversal_path):
        print(f"Step {step+1}: {title} - {link}")

def main():
    start_url = "https://en.wikipedia.org/wiki/Lionel_Messi"
    end_url = "https://en.wikipedia.org/wiki/Donald_Trump"
    
    print("Naive Traversal using Random Links:")
    naive_traversal(start_url, end_url)
    print("Smart Traversal using Embeddings:")
    embedding_traversal(start_url, end_url)

if __name__ == "__main__":
    main()

