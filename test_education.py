from backend.services.scraper.education_scraper import EducationScraper
from backend.utils.http_client import HttpClient

es = EducationScraper(http_client=HttpClient())
pe = es.get_profile_endpoints_from_people("https://education.virginia.edu/about/directory?type=11&department=All&program=All&page=")
print(pe)
print(len(pe))
print("-----PROFILE DATA-----")
print(es.get_name_from_profile(pe[0]))
print(es.get_emails_from_profile(pe[0]))
# print(es.get_about_from_profile(pe[0]))
# print(es.get_research_interests_from_profile(pe[0]))