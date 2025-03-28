
import requests # type: ignore
import re
from bs4 import BeautifulSoup # type: ignore

def extract_meta_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Get Meta Description
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and meta_tag.get("content"):
                return meta_tag["content"]

            # If Meta Description is missing, use Page Title
            title_tag = soup.find("title")
            if title_tag:
                return title_tag.text

    except requests.exceptions.RequestException:
        return None

    return None


def extract_text_from_url(url):
    """Extract meaningful words from the URL (excluding 'www', 'com', etc.)."""
    url = url.lower()
    url = re.sub(r"(https?://)?(www\.)?", "", url)  # Remove protocol & 'www'
    url = re.sub(r"[^\w\s]", " ", url)  # Replace non-alphanumeric with spaces
    return url


if __name__=="__main__":
    url="https://www.youtube.com"
    print(extract_meta_data(url))
    print(extract_text_from_url(url))
    