from husky.api import nasdaq
import requests
from husky.utils import utility

def pre_market_validator(page_url):
    headers = {
        "user-agent" : utility.random_ua()
    }
    r = requests.get(page_url, headers=headers)
    if r.status_code != 200:
        return None
    return nasdaq.parse_time_quote_slice_page(r.content)

if __name__ == "__main__":
    for i in range(1,12):
        print pre_market_validator(nasdaq.real_time_quote_slice_url("baba", i, 1))
