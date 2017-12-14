import requests
import json


def convert_message(msg):
    ret = { }
    if 'title' in msg:
        ret['title'] = msg['title']

    if 'author' in msg:
        ret['authors'] = [ '{} {}'.format(a['given'], a['family']) for a in msg['author'] ]

    if 'container-title' in msg:
        ret['journal'] = msg['container-title'][0]

    if 'volume' in msg:
        ret['volume'] = msg['volume']

    if 'page' in msg:
        ret['page'] = msg['page']

    if 'published-print' in msg:
        ret['year'] = msg["published-print"]["date-parts"][0][0]

    return ret


def query_crossref(query, raw=False):
    # Requested by crossref API
    headers = {
        'User-Agent': 'BSECuration 1.0 (mailto:bpp4@vt.edu)'
    }

    r = requests.get('https://api.crossref.org/works', params={'query': query}, headers=headers)
    if r.status_code != 200:
        return None
    else:
        j = json.loads(r.text)
        if raw:
            return j
        else:
            return convert_message(j['message']['items'][0])


def query_crossref_doi(doi, raw=False):
    # Requested by crossref API
    headers = {
        'User-Agent': 'BSECuration 1.0 (mailto:bpp4@vt.edu)'
    }

    r = requests.get('https://api.crossref.org/works/' + doi, headers=headers)
    if r.status_code != 200:
        return None
    else:
        j = json.loads(r.text)
        if raw:
            return j
        else:
            return convert_message(j['message'])
