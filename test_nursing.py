from backend.services.scraper.nursing_scraper import NursingScraper
from backend.utils.http_client import HttpClient

ns = NursingScraper(http_client=HttpClient())
pe = ns.get_profile_endpoints_from_people("https://nursing.virginia.edu/research/faculty-research/")
print(pe)
print(len(pe))
print("-----PROFILE DATA-----")
print(ns.get_name_from_profile(pe[0]))
print(ns.get_emails_from_profile(pe[0]))
print(ns.get_about_from_profile(pe[0]))
print(ns.get_research_interests_from_profile(pe[0]))