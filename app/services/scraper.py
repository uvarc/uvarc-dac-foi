from app.utils.constants import SEAS_DEPARTMENTS
from app.utils.constants import NO_RESULTS_DIV
from app.utils.constants import CONTACT_BLOCK_NAME_A_TAG

import requests
from lxml import html

class DepartmentScraper:
    def __init__(self):
        pass

    def scrape_dept_info(self, department, url):
        profile_urls = self.extract_faculty_profile_urls(url)

    def extract_faculty_profile_urls(self, url):
        i = 0
        page_urls = []

        while True:
            page_url = f"{url}{i}"
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Could not fetch webpage\nStatus Code: {response.status_code}")
            tree = html.fromstring(response.content)
            no_results = tree.xpath(NO_RESULTS_DIV)
            if no_results:
                break
            links = tree.xpath(CONTACT_BLOCK_NAME_A_TAG)
            for link in links:
                page_urls.append(link)
            i += 1
        return page_urls

