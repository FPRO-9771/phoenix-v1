import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Base URL of the CTR Electronics Phoenix 6 Python API documentation
BASE_URL = "https://api.ctr-electronics.com/phoenix6/latest/python/"
DOWNLOAD_FOLDER = "ctr_phoenix6_docs"

# Create a folder to store downloaded files
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_all_links(base_url):
    """Crawl the base URL and extract all internal documentation links."""
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to retrieve {base_url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = set()

    # Extract all anchor tags with href attributes
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        
        # Filter only internal documentation links
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)

    return list(links)

def download_page(url):
    """Download and save an HTML page locally."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Extract filename from URL
            filename = urlparse(url).path.strip("/").replace("/", "_") + ".html"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename if filename else "index.html")

            with open(filepath, "w", encoding="utf-8") as file:
                file.write(response.text)
            
            print(f"Downloaded: {url} → {filename}")
        else:
            print(f"Failed to download {url} (Status Code: {response.status_code})")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Get all documentation links
all_links = get_all_links(BASE_URL)

# Download each page
for link in all_links:
    download_page(link)

print("\n✅ All documentation pages downloaded successfully!")
