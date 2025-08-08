from datetime import date
from backend.services.nsf.nsf_proxy import NSFProxy
from backend.services.nsf.nsf_service import NSFService
from backend.utils.http_client import HttpClient
import pandas as pd

if __name__ == "__main__":
    fname = "Chris"
    lname = "Paolucci"
    pr = NSFProxy()

    # print(len(pr.call_nsf_api(payload={
    #         "coPDPI": fname + " " + lname,
    #         "expDateStart": date.today().strftime("%m/%d/%Y"), # date format: 11/02/2023
    #     })))
    
    nsf_service = NSFService(proxy=pr)
    df = nsf_service.compile_project_metadata(pi_first_name=fname, pi_last_name=lname)
    print(df.shape)
    print(df.head())
    print(type(df.loc[0]["date"]))