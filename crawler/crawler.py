import requests
from bs4 import BeautifulSoup, NavigableString
import sqlite3
from urllib.parse import urljoin, urlparse
import time
from dotenv import load_dotenv
import os
import re
from urllib import robotparser

load_dotenv()

DOMAINS = os.getenv("DOMAINS", "").split(",")

MAX_PAGES_PER_DOMAIN = int(os.getenv("MAX_PAGES_PER_DOMAIN", 50))

#init sql db
def init_db(): 
    conn = sqlite3.connect("crawler/crawled_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            snippet TEXT
        )
    """)
    conn.commit()
    return conn


def is_allowed_by_robots(url, user_agent="MyMiniSearchEngine"):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)

    try:
        rp.read()
    except Exception as e:

        return True

    return rp.can_fetch(user_agent, url)

#function to crawl page
def crawl_page(url, domain, conn):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(["script", "style"]):
            tag.extract()


        title = soup.title.string if soup.title else "No title"
        main_content = soup.body if soup.body else soup

        text_chunks = []
        for element in main_content.descendants:
            if isinstance(element, NavigableString):
                text = element.strip()
                if text:
                    text_chunks.append(text)
        
        full_text = " ".join(text_chunks)

        full_text = re.sub(r"[^a-zA-Z0-9\s]", "", full_text)

        full_text = re.sub(r"\s+", " ", full_text)
        snippet = full_text if soup.body else ""

        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO pages (domain, url, title, snippet)
            VALUES (?, ?, ?, ?)
        """, (domain, url, title, snippet))
        
        conn.commit()

        print(f"Inserted into DB: URL={url}, Title={title}, Snippet={snippet[:10]}...")
        print(f"Successfully crawled {url}")
        return soup

    except requests.RequestException as e:
        print(f"failed to crawl {url}: {e}")
    except Exception as e:
        print(f"An error occured: {e}")
        return None

def is_allowed_url(url, allowed_domains):
    domain = urlparse(url).netloc
    return any(domain.endswith(allowed_domain) for allowed_domain in allowed_domains)

def crawl_domain(start_url, allowed_domain, max_pages=10000):
    visited = set()
    to_visit = [start_url]
    base_domain = urlparse(start_url).netloc
    conn = init_db()
    pages_crawled = 0

    try:
        while len(to_visit) > 0 and pages_crawled < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue     
            if not is_allowed_by_robots(url):
                print(f"[ROBOTS] Disallowed by robots.txt: {url}")
                continue 
            try:
                soup = crawl_page(url, base_domain, conn)
                visited.add(url)
                pages_crawled += 1
                ## find and queue internal links
                if soup:
                    for link in soup.find_all("a", href=True):
                        full_url = urljoin(start_url, link["href"])
                        parsed_url = urlparse(full_url)

                        if parsed_url.netloc == base_domain and is_allowed_url(full_url, [allowed_domain]) and full_url not in visited:
                            to_visit.append(full_url)
                
                ## pause execution, will be reviewed
                time.sleep(1)
            except Exception as e:
                print(f"Failed to crawl {url}: {e}")
            
    except Exception as e:
        print(f"An error occured while crawling domain:${e}")
    
    finally:
        conn.close()
        print(f"Crawled {len(visited)} pages from {base_domain}")

def crawl_all_domains():

    for domain in DOMAINS:
        domain = domain.strip()
        start_url = f"https://{domain}"
        print(f"Starting crawl for {domain} {start_url}...")
        crawl_domain(start_url, allowed_domain=domain, max_pages=MAX_PAGES_PER_DOMAIN)

if __name__ == "__main__":
    if not DOMAINS:
        print("Please add a list of domains to the env file under DOMAINS")
    else:
        crawl_all_domains()