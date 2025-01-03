import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from urllib.parse import urljoin, urlparse
import time



#init sql db
def init_db(): 
    conn = sqlite3.connect("crawler/crawled_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            snippet TEXT
        )
    """)
    conn.commit()
    return conn

#function to crawl page
def crawl_page(url, base_domain, conn):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else "No title"
        snippet = " ".join(list(soup.body.stripped_strings)[:50]) if soup.body else "No content"


        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO pages (url, title, snippet)
            VALUES (?, ?, ?)
        """, (url, title, snippet))
        
        conn.commit()
        # with open("crawler/crawled_data.json", "w") as file:
        #     json.dump([result], file, indent=4)

        print(f"Inserted into DB: URL={url}, Title={title}, Snippet={snippet[:30]}...")
        print(f"Successfully crawled {url}")
        return soup
        
    except requests.RequestException as e:
        print(f"failed to crawl {url}: {e}")
    except Exception as e:
        print(f"An error occured: {e}")
        return None

def crawl_domain(start_url, max_pages=100):
    visited = set()
    to_visit = [start_url]
    base_domain = urlparse(start_url).netloc
    conn = init_db()

    try:
        while len(to_visit) > 0 and len(visited) < max_pages:
            url = to_visit.pop(0)
            print(f"{len(to_visit)}")
            if url in visited:
                continue
            
            soup = crawl_page(url, base_domain, conn)
            visited.add(url)
            ## find and queue internal links
            if soup:
                for link in soup.find_all("a", href=True):
                    full_url = urljoin(start_url, link["href"])
                    parsed_url = urlparse(full_url)

                    if parsed_url.netloc == base_domain and parsed_url not in visited:
                        to_visit.append(full_url)
            
            ## pause execution, will be reviewed
            time.sleep(2)
            
    except Exception as e:
        print(f"An error occured while crawling domain:${e}")
    
    finally:
        conn.close()
        print(f"Crawled {len(visited)} pages from {base_domain}")




if __name__ == "__main__":
    test_url = "https://angular.io"
    crawl_domain(test_url, max_pages=10)