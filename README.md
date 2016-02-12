# Cheap Domain Finder

A Python helper to find cheap domains faster on [namecheap.com](https://www.namecheap.com/)


## Usage

Install dependencies first: :lipstick:

```bash
pip3 install -r requirements.txt
```

Edit the script, i.e. [cheap-domain-finder.py](cheap-domain-finder.py), to put your desired keywords: :thought_balloon:

```python
keywords = [ "code", "note", "git" ]
```

Finally, run it with Python3! :checkered_flag:


## Nota Bene

Three types of domains are available, and those marked as **inactive** are cheapest and affordable. :joy:

For the **premium** domains, HTTP GET request to endpoint like `https://domainsearch.namecheapapi.com/domain/note.host` will tell you the price in USD. :dollar:
