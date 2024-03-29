#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
from requests import get, codes
from urllib import parse
from json import loads, dump


keywords = [ "pad", "draft", "drafts", "notepad", "text", "sketch", "memo", "editor", "vim", "code", "note", "git", "github" ]
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


def retrieve_content(keyword, retry_times):
    url = page_url % keyword
    while retry_times > 0:
        content = fetch_page(url)
        retry_times -= 1
        if content != None:
            try:
                return BeautifulSoup(content, "html5lib")
            except Exception as e:
                pass
    return None


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


def query_batch(client_id, keyword, batch_list, retry_times):
    query_list = [ keyword + "." + tld for tld in batch_list ]
    query_string = parse.quote(",".join(query_list))
    url = api_batch_url % (client_id, query_string)
    while retry_times > 0:
        content = fetch_page(url)
        retry_times -= 1
        if content != None:
            try:
                return loads(content)
            except Exception as e:
                pass
    return None


def query_all_domains(keyword):
    page_soup = retrieve_content(keyword, retry_times)
    if page_soup == None:
        return None
    client_id = parse_client_id(page_soup)
    tld_list = parse_tld_list(page_soup)

    domains = {}
    tld_sublist = [ tld_list[x : x+domain_per_query] for x in range(0, len(tld_list), domain_per_query) ]
    for tlds in tld_sublist:
        result = query_batch(client_id, keyword, tlds, retry_times)
        for item in result["status"]:
            summary = item["summary"]
            domain = item["domain"]
            if summary in ["premium", "reserved", "inactive"]:
                if domain not in domains:
                    domains[domain] = summary
                    print(domain, summary)
    return domains


if __name__ == '__main__':
    for keyword in keywords:
        domains = query_all_domains(keyword)
        with open("domains-" + keyword + ".json", 'w') as file:
            dump(domains, file, sort_keys = True, indent = 2, ensure_ascii = False)
