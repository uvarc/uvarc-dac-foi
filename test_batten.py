from backend.services.scraper.batten_scraper import BattenScraper
from backend.utils.http_client import HttpClient
from backend.utils.http_client_cached import HttpClientCached

bs = BattenScraper(http_client=HttpClientCached())
pe = bs.get_profile_endpoints_from_people("https://batten.virginia.edu/faculty-research/faculty/")
print(pe)
print(len(pe))
print("-----PROFILE DATA-----")
print("Emails:", bs.get_emails_from_profile(pe[0]))
print("Name:", bs.get_name_from_profile(pe[0]))
print("About:", bs.get_about_from_profile(pe[0]))
print("Research Interests:", bs.get_research_interests_from_profile(pe[0]))