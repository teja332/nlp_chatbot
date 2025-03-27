from bs4 import BeautifulSoup
import requests

def scrape_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text()
        else:
            return "Failed to fetch website."
    except Exception as e:
        return f"Error: {str(e)}"
