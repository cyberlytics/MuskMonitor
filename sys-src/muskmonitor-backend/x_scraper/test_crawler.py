import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import json
from urllib.robotparser import RobotFileParser

def is_crawl_allowed(url):
    parsed_url = urlparse(url)
    robots_url = urljoin(f"{parsed_url.scheme}://{parsed_url.netloc}", "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch("*", url)

def crawl(url):
    #if not is_crawl_allowed(url):
    #    print(f"Crawling not allowed for {url}")
    #    return None, None

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    url_text = soup.get_text()
    all_links = [a['href'] for a in soup.find_all('a', href=True)]
    
    return url_text, all_links

def crawl_with_links(url, link_pattern, n_links=20):
    #if not is_crawl_allowed(url):
    #    print(f"Crawling not allowed for {url}")
    #    return None, None

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    url_text = soup.get_text()
    all_links = [a['href'] for a in soup.find_all('a', href=True)]
    
    link_texts = [link for link in all_links if re.match(link_pattern, link)]
    link_texts = link_texts[:n_links]
    
    return url_text, link_texts

if __name__ == "__main__":
    filename = "https://nitter.privacydev.net/elonmusk"
    text, links = crawl(filename)

    if text and links:
        print("TEXT")
        print(text)
        print()
        print("LINKS")
        print(links)

