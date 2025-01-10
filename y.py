import os
import requests

AIRTABLE_KEY = "patiAsX1sScyiVAUg.eefefb31e2cbedc165708ecfad89e05f35a797c1e3f1ede26b4857d64e65cd05"
ADMIN_KEY = "pat0xJX8l8mXI1GAn.7bb41c943b7ebbd1e291ebee52bdcb6203e447895604d4a4a123ef9ef22f3044"

headers = {"Authorization": f"Bearer {ADMIN_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.airtable.com/v0"

baseId = "appiADB3LyPovCX2R"
tableId = "tblzYNCHeZvI15U5l"
tables_path = f"/meta/bases/{baseId}/tables"
bases_path = "/meta/bases"
table_path = f"/{baseId}/{tableId}"

def make_request(path, method="GET", payload={}):

    _request = requests.get if method == "GET" else requests.post

    kwargs = {
        "url": BASE_URL + path,
        "headers": headers
    }

    if method == "POST":
        kwargs["json"] = payload

    response = _request(**kwargs)

    print(response.status_code)
    print(response.json())

make_request(table_path)

# payload = {
#     "records": [
#         {
#             "fields": {
#                 "Name": "Union Square",
#                 "Flagged": True
#             }
#         },
#         {
#             "fields": {
#                 "Name": "Ferry Building"
#             }
#         }
#     ]
# }


# make_request(table_path, "POST", payload)