#!/usr/bin/env python3
#
# html generator for team protocols
#
# (c) 2015 Daniel Jankowski

import json
import re
import urllib.request
import urllib.parse
import http.cookiejar
import colorama
from colorama import Fore, Back, Style


BASE_URL = 'http://linux-statt-windows.org/api/'
SLUGS = ['111/team-protokoll']
COOKIE = ""


def authenticate():
    cj = http.cookiejar.CookieJar()
    c = http.cookiejar.Cookie(version=0, name='express.sid', value=COOKIE, port=None, port_specified=False, domain='linux-statt-windows.org', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1453671824, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(c)
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def fetch_category(opener, table, not_working_urls):
    log('fetched content-table')

    for t in table:
        log('fetching ' + t['title'])
        d = fetch_data(opener, BASE_URL + 'topic/' + str(t['slug']))
        if d == None:
            log_error('failed to fetch')
            not_working_urls.append(t['slug'])
        else:
            print(d['posts'][0]['content'])
    return not_working_urls


def fetch_data(opener, url):
    try:
        rqst = opener.open(url)
        data = json.loads(rqst.read().decode('utf-8'))
    except Exception as e:
        data = None
    return data


def fetch_content_table(opener, slug):
    rqst = opener.open(BASE_URL + 'api/category/' + slug)
    data = json.loads(rqst.read().decode('utf-8'))
    topics = data['topics']
    table = []
    for t in topics:
        table.append({'title':t['title'], 'slug':t['slug']})
    return table


def log(text):
    print(Fore.GREEN + '==>' + Fore.WHITE + ' ' + text)


def log_error(text):
    print(Fore.RED + '==>' + Fore.WHITE + ' ' + text)


def main():
    colorama.init()
    log('trying to authenticate')
    opener = authenticate()
    log('Success! Authenticatd')
   
    not_working_urls = []

    for slug in SLUGS:
        table = fetch_content_table(opener, slug)
        log('fetched content-table')

        not_working_urls = fetch_category(opener, table, not_working_urls)

    log('not working slugs')
    print(not_working_urls)
    return


if __name__ == '__main__':
    main()
