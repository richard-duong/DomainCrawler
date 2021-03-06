import os
import sys
import time
import pickle

import requests
from itertools import combinations

from logger import Logger

# combinations resource:
# https://stackoverflow.com/questions/32789338/how-to-get-all-combinations-of-several-letters-in-python

# daemon resource: 
# https://www.childs.be/blog/post/how-to-run-a-python-script-as-a-service-in-background-as-a-daemon

# domain name rules:
# https://whogohost.com/host/knowledgebase/308/Valid-Domain-Name-Characters.html#:~:text=For%20domain%20names%20to%20be%20valid%2C%20domain%20names,include%20a%20space%20%28e.g.%20...%20More%20items...%20

CONFIG = "config.ini"
DATA_PATH = "data"
LOG_PATH = "logs/crawl"
CHECKED = "checked.pkl"

BASE_URL = "https://api.ote-godaddy.com"
VERSION = "v1"


# EXTENSIONS = ["com", "net", "org", "edu", "biz", "gov", "mil", "info", "name", "me", "tv", "us", "mobi"]
EXTENSIONS = ["com", "net"]
CHARS = "abcdefghijklmnopqrstuvwxyz0123456789-"

MIN_DOMAIN_SIZE = 3
MAX_DOMAIN_SIZE = 63
WAIT_TIME = 1

sys.stdout = Logger(LOG_PATH)


# retrieve key and secret
if os.path.isfile(f"{CONFIG}"): 
    with open(f"{CONFIG}", "r") as configFile:
        api_key = configFile.readline().split()[1]
        api_secret = configFile.readline().split()[1]
        headers = {"Authorization": f"sso-key {api_key}:{api_secret}"}
else:
    print(f"""No config file found!, please make a config.ini file that has this format:
           
           config.ini:
           key, [API-KEY]
           secret, [API-SECRET]

           To get your key and secret from godaddy.com, use this url: https://developer.godaddy.com/getstarted 
           Make sure you make a key under the OTE environment hosted at: https://api.ote-godaddy.com""")
    sys.exit()



# build directories
for ext in EXTENSIONS:
    try:
        os.makedirs(f"{DATA_PATH}/{ext}")
    except FileExistsError:
        pass



# open checked set
if os.path.isfile(f"{DATA_PATH}/{CHECKED}"):
    with open(f"{DATA_PATH}/{CHECKED}", "rb") as checkedFile:
        checked = pickle.load(checkedFile)
else:
    checked = set()
print(f"Loaded {len(checked)} visited domains")



# try all combinations and append to domains
count = 0
for i in range(MIN_DOMAIN_SIZE, MAX_DOMAIN_SIZE):

    print(f"Start creating domains for: {i} characters")
    domains = list(combinations(CHARS*i, i))
    domains = list(set(["".join(domain) for domain in domains]))
    print(f"Finish creating {len(domains)} domains for: {i} characters")
    domains = [domain for domain in domains if domain not in checked]
    print(f"Remove visited with {len(domains)} domains remaining for: {i} characters")

    for domain in domains:

        # skip if non-qualifying domain
        if domain.startswith("-") or domain.endswith("-") or domain.find("--") != -1 or domain in checked:
            continue
        for ext in EXTENSIONS:  
            count += 1
            successful = False
            while not successful:
                page = requests.get(f"{BASE_URL}/{VERSION}/domains/available?domain={domain}.{ext}", headers=headers)
                if page.status_code == 422:
                    print(f"{count}. invalid body on: {domain}.{ext}")
                    successful = True
                elif page.status_code == 400:
                    print(f"{count}. request was malformed on: {domain}.{ext}")
                    successful = True
                elif page.status_code == 401:
                    print(f"{count}. authentication info not sent or invalid on: {domain}.{ext}")
                    sys.exit()
                elif page.status_code == 403:
                    print(f"{count}. authenticated user not allowed access on: {domain}.{ext}")
                    sys.exit()
                elif page.status_code == 429:
                    print(f"{count}. too many requests on: {domain}.{ext}")
                    successful=False
                elif page.status_code == 200 and page.json()["available"] == True:
                    with open(f"{DATA_PATH}/{ext}/size{str(i)}.txt", "a") as outFile:
                        outFile.write(f'{domain}.{ext} ${page.json()["price"]}\n')
                    print(f"{count}. available on: {domain}.{ext}")
                    successful=True
                elif page.status_code == 200:
                    print(f"{count}. not available on: {domain}.{ext}")
                    successful=True
                else:
                    print(f"{count}. unknown code {page.status_code}: {domain}.{ext}")
                    successful=True
                checked.add(domain)
                with open(f"{DATA_PATH}/{CHECKED}", "wb") as checkedFile:
                    pickle.dump(checked, checkedFile)
                time.sleep(WAIT_TIME)



