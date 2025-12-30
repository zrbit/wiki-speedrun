from bs4 import BeautifulSoup
import requests
import sqlite3
import random
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
import time
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


BASE_URL = 'https://en.wikipedia.org'
model = SentenceTransformer("all-MiniLM-L6-v2")
model_2 = SentenceTransformer("all-mpnet-base-v2")
session = requests.Session()

session.headers.update({
    "User-Agent": "WikiSpeedrun/1.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})


def get_html_content(url):
    try:
        response = session.get(url,timeout=20)
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
        if a.has_attr("href") and a['href'].startswith("/wiki/") and not a['href'].startswith("/wiki/Special:") and not a['href'].startswith("/wiki/Help:") and not a['href'].startswith("/wiki/Wikipedia:") and not a['href'].startswith("/wiki/Category:") and not a['href'].startswith("/wiki/File:") and not a['href'].startswith("/wiki/Template:") and not a['href'].startswith("/wiki/Portal:") and not a['href'].startswith("/wiki/Main_Page") :
            links.append(BASE_URL + a["href"])
            titles.append(a.get("title", "No title"))
    return titles, links

def naive_traversal(start_url, end_url):
    start_time = time.time()
    found = False
    html = get_html_content(start_url)
    
    link_count = 0
    traversal_path = []

    while True:
        if html:
            soup = BeautifulSoup(html, "html.parser")
            titles, links = get_links_and_titles(soup)
            if end_url in links:
                found = True
                break
            else:
                if not links:
                    break
                rand_index = random.randint(0, len(links)-1)
                next_link = links[rand_index]
                traversal_path.append(next_link)
                html = get_html_content(next_link)
                link_count += 1
            if link_count>40:
                found = False
                break
    end_time = time.time()
    return end_time - start_time, link_count, traversal_path, found

def embedding_traversal(start_url, end_url):    
    start_time = time.time()
    found = False
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
                found = True
                break
            else:
                if not links:
                    break
                filtered_links = []
                filtered_titles = []
                for link, title in zip(links, titles):
                    if link not in traversal_path:
                        filtered_links.append(link)
                        filtered_titles.append(title)
                links = filtered_links
                titles = filtered_titles

                embeds = model.encode(titles, convert_to_numpy=True)                
                #compute cosine similarity
                cosine_similarities = [dot(embed, end_embed)/(norm(embed)*norm(end_embed)) for embed in embeds]
                max_index = cosine_similarities.index(max(cosine_similarities))
                next_link = links[max_index]
                traversal_path.append(next_link)
                html = get_html_content(next_link)
                link_count += 1
            if link_count>40:
                found = False
                break
    end_time = time.time()
    return end_time - start_time, link_count, traversal_path,found


def better_embedding_traversal(start_url, end_url):    
    start_time = time.time()
    found = False
    html = get_html_content(start_url)
    
    link_count = 0
    traversal_path = set()
    end_title = end_url.split("/wiki/")[-1].replace("_", " ")
    end_embed = model.encode([end_title], convert_to_numpy=True)[0]
    end_arr  = np.array(end_embed)
    end_norm = np.linalg.norm(end_arr)

    end_embed_2 = model_2.encode([end_title], convert_to_numpy=True)[0]
    end_arr_2  =  np.array(end_embed_2)
    end_norm_2 = np.linalg.norm(end_arr_2)
    while True:
        if html:
            soup = BeautifulSoup(html, "html.parser")
            titles, links = get_links_and_titles(soup)
            if end_url in links:
                found = True
                break
        
            else:
                if not links:
                    break
                # Filter out already visited links
                filtered_links = []
                filtered_titles = []
                for link, title in zip(links, titles):
                    if link not in traversal_path:
                        filtered_links.append(link)
                        filtered_titles.append(title)

                links = filtered_links
                titles = filtered_titles
                embeds = model.encode(titles, convert_to_numpy=True)
                embeds_arr = np.array(embeds)                
                dot_products = embeds_arr @ end_arr
                norms = np.linalg.norm(embeds_arr, axis=1)
                cosine_similarities = dot_products / (norms * end_norm)

                embeds_2 = model_2.encode(titles, convert_to_numpy=True)
                embeds_arr_2 = np.array(embeds_2)                
                dot_products_2 = embeds_arr_2 @ end_arr_2
                norms_2 = np.linalg.norm(embeds_arr_2, axis=1)
                cosine_similarities_2 = dot_products_2 / (norms_2 * end_norm_2)

                cosine_similarities = (cosine_similarities + cosine_similarities_2) / 2
                chosen_index = np.argmax(cosine_similarities)
                next_link = links[chosen_index]
                traversal_path.add(next_link)
                html = get_html_content(next_link)
                link_count += 1
            if link_count>40:
                found = False
                break
    end_time = time.time()
    return end_time - start_time, link_count, traversal_path,found


def main():
    
    start_url = "https://en.wikipedia.org/wiki/Lionel_Messi"
    end_url = "https://en.wikipedia.org/wiki/Potato"
    
    print("Traversal using Embeddings:")
    time, link, path = embedding_traversal(start_url, end_url)
    print(f"Time taken: {time} seconds, Links followed: {link}")

    print("Smart Traversal using Embeddings:")
    time, link, path = better_embedding_traversal(start_url, end_url)
    print(f"Time taken: {time} seconds, Links followed: {link}")
    
        

if __name__ == "__main__":
    main()

