#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
from requests import get, codes
from urllib import parse
from json import loads, dump

keyword = "note"
page_url = "https://www.namecheap.com/domains/registration/results.aspx?domain=%s"
api_batch_url = "https://api.domainr.com/v2/status?client_id=%s&domain=%s"
retry_times = 3
timeout_secs = 10
domain_per_query = 5


def fetch_page(url):
    try:
        resp = get(url, timeout = timeout_secs)
        if resp.status_code == codes.ok:
            return resp.text
    except Exception as e:
        pass


def retrieve_content(retry_times):
    url = page_url % keyword
    while retry_times > 0:
        content = fetch_page(url)
        if content == None:
            content = ""
            retry_times -= 1
        else:
            retry_times = 0
    return BeautifulSoup(content, "html5lib")


def parse_tld_list(page_soup):
    tld_tags = page_soup.select(".domain-filter-form .fieldset input")
    tld_list = [ tag.get("value") for tag in tld_tags ]
    tld_list.sort()
    return tld_list


def parse_client_id(page_soup):
    pattern = re.compile(u"var\sCLIENT_ID\s=\s'(.*?)'")
    script_tags = page_soup.select("script[type=text/javascript]")
    for tag in script_tags:
        tag_string = tag.string
        if tag_string is None:
            continue
        result = pattern.search(tag_string)
        if result:
            return result.group(1)
    else:
        return None


def query_batch(client_id, batch_list, retry_times):
    query_list = [ keyword + "." + tld for tld in batch_list ]
    query_string = parse.quote(",".join(query_list))
    url = api_batch_url % (client_id, query_string)
    while retry_times > 0:
        content = fetch_page(url)
        if content == None:
            content = ""
            retry_times -= 1
        else:
            retry_times = 0
    return loads(content)


page_soup = retrieve_content(retry_times)
client_id = parse_client_id(page_soup)
tld_list = parse_tld_list(page_soup)

domains = {}
tld_sublist = [ tld_list[x : x+domain_per_query] for x in range(0, len(tld_list), domain_per_query) ]
for tlds in tld_sublist:
    result = query_batch(client_id, tlds, retry_times)
    for item in result["status"]:
        summary = item["summary"]
        domain = item["domain"]
        if summary in ["premium", "reserved", "inactive"]:
            if domain not in domains:
                domains[domain] = summary
                print(domain, summary)

with open("domains.json", 'w') as file:
    dump(domains, file, sort_keys = True, indent = 2, ensure_ascii = False)
