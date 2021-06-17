import requests
CONFIG = "config.ini"
BASE_URL = "https://api.ote-godaddy.com/v1/domains/available?domain={domain}"
domains=["google.com", "bing.com", "yahoo.com"]

# retrieve key and secret
with open(f"{CONFIG}", "r") as configFile:
    api_key = configFile.readline().split()[1]
    api_secret = configFile.readline().split()[1]
    headers = {"Authorization": f"sso-key {api_key}:{api_secret}"}


for domain in domains: 
    page = requests.get(BASE_URL.format(domain=domain), headers=headers)
    if page.status_code == 200:
        print(domain, page.json()["available"])
