#This script fetches a list of all interesting Wikipedia page links from the "Popular pages" special page. It stores the titles and links in a SQLite database.
#DB from this will be used to fetch popular articles for speedrunning.
from bs4 import BeautifulSoup
import requests
import sqlite3


BASE_URL = 'https://en.wikipedia.org'

# Create a reusable session with headers
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

def init_db():
    #initialize the database if needed, make a table popular_links with columns id, title, link
    conn = sqlite3.connect('wiki_links.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS popular_links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, link TEXT)''')
    conn.commit()
    conn.close()

def insert_links(titles, links):
    conn = sqlite3.connect('wiki_links.db')
    c = conn.cursor()
    for title, link in zip(titles, links):
        c.execute("INSERT INTO popular_links (title, link) VALUES (?, ?)", (title, link))
    conn.commit()
    conn.close()

def remove_db_table():
    conn = sqlite3.connect('wiki_links.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS popular_links")
    conn.commit()
    conn.close()


def main():
    start_url = "https://en.wikipedia.org/wiki/Wikipedia:Popular_pages" 
    html = get_html_content(start_url)
    
    if html:
        soup = BeautifulSoup(html, "html.parser")
        all_links_element = soup.find_all("td")
        links = []
        title = []
        for td in all_links_element:
            a = td.find("a")
            if a and a.get("href") and a.get("title"):
                links.append(BASE_URL + a["href"])
                title.append(a["title"])
        insert_links(title, links)
          
if __name__ == "__main__":
    init_db()
    main()
