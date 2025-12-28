#This script fetches a list of all Wikipedia page links by navigating through the "All Pages" special page. It stores the titles and links in a SQLite database.
#I limit rn to 1024 iterations to avoid excessive data fetching.
#DB from this will be used to fetch random articles for speedrunning.

from bs4 import BeautifulSoup
import requests
import sqlite3


BASE_URL = 'https://en.wikipedia.org'
NUMER_OF_ITERATION = 1024



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
    #initialize the database if needed, make a table random_links with columns id, title, link
    conn = sqlite3.connect('wiki_links.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS random_links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, link TEXT)''')
    conn.commit()
    conn.close()

def insert_links(titles, links):
    conn = sqlite3.connect('wiki_links.db')
    c = conn.cursor()
    for title, link in zip(titles, links):
        c.execute("INSERT INTO random_links (title, link) VALUES (?, ?)", (title, link))
    conn.commit()
    conn.close()



def main():
    start_url = "https://en.wikipedia.org/wiki/Special:AllPages" #you can change the starting point if needed, but this is the default
    i = 0
    while i<NUMER_OF_ITERATION:
        html = get_html_content(start_url)
        
        if html:
            soup = BeautifulSoup(html, "html.parser")
            next_page = soup.find_all("div",class_ = "mw-allpages-nav")[0].text
            if "Next page" in next_page and "Previous page" not in next_page:
                start_url = BASE_URL + soup.find_all("div",class_ = "mw-allpages-nav")[0].contents[0]['href']
            else:
                start_url = BASE_URL + soup.find_all("div",class_ = "mw-allpages-nav")[0].contents[2]['href']
            inside_page_link = soup.find("div",class_='mw-allpages-body')
            
            links = []
            title = []
            for li in inside_page_link.find_all("li"):
                a = li.find("a")
                if a and a.get("href") and a.get("title"):
                    links.append(BASE_URL + a["href"])
                    title.append(a["title"])
            insert_links(title, links)
        i+=1
                
if __name__ == "__main__":
    init_db()
    main()
