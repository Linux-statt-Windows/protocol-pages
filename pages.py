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
from html.parser import HTMLParser

BASE_URL = 'http://linux-statt-windows.org/api/'
SLUGS = ['111/team-protokoll', '111/team-protokoll?page=2']
COOKIE = ""
DEST = './Pages/'

# Refurbish data

class html_parser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.__is_title = False
        self.titles = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self.__is_title = True

    def handle_data(self, data):
        if self.__is_title:
            self.__is_title = False
            self.titles.append(data)


def generate_toc(toc, titles):
    doc = '<!DOCTYPE html>\n<head><link rel="stylesheet" href="./style.css"></head><body>'
    doc += '<center><h1>Team-Handbuch</h1></center><br /><h3>Inhaltsverzeichnis</h3><ul>'
    for t in titles:
        doc += '<li><a href="./' + t + '.html">' + toc[t][0] + '</a></li><ul>'
        #print(toc[t][0])
        for x in toc[t][1]:
            doc += '<li>' + x + '</li>'
            #print('--' + x)
        doc += '</ul>'
    doc += '</ul></body>'
    save_page(doc, 'toc')
    return

# File handler

def save_page(data, title):
    with open(DEST + title + '.html', 'w') as fp:
        fp.write(data)


# User authentication

def authenticate():
    cj = http.cookiejar.CookieJar()
    c = http.cookiejar.Cookie(version=0, name='express.sid', value=COOKIE, port=None, port_specified=False, domain='linux-statt-windows.org', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1453671824, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(c)
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


# Fetch functions

def fetch_category(opener, table, not_working_urls, toc, titles):
    parser = html_parser()
    for t in table:
        log('fetching ' + t['title'])
        d = fetch_data(opener, BASE_URL + 'topic/' + str(t['slug']))
        if d == None:
            log_error('failed to fetch')
            not_working_urls.append(t['slug'])
        else:
            # save to file
            html = '<!DOCTYPE>\n<html>\n<head><link rel="stylesheet" href="./style.css"></head>\n<body><center><h1>' + t['title'] + '</h1></center>''<a href="./toc.html">../Inhaltsverzeichnis</a><hr />'
            html += d['posts'][0]['content']
            html += '</body>'
            save_page(html, t['title'])
            
            parser.feed(html)
            titles.append(t['title'])
            toc[t['title']] = (t['title'], parser.titles)
            parser.titles = []
    return not_working_urls, toc, titles


def fetch_data(opener, url):
    try:
        rqst = opener.open(url)
        data = json.loads(rqst.read().decode('utf-8'))
    except Exception as e:
        data = None
    return data


def fetch_content_table(opener, slug):
    rqst = opener.open(BASE_URL + 'category/' + slug)
    data = json.loads(rqst.read().decode('utf-8'))
    topics = data['topics']
    table = []
    for t in topics:
        table.append({'title':t['title'], 'slug':t['slug']})
    return table


# Log functions

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
    toc, titles = {}, []

    for slug in SLUGS:
        log('fetched content-table')
        table = fetch_content_table(opener, slug)
        not_working_urls, toc, titles = fetch_category(opener, table, not_working_urls, toc, titles)
    generate_toc(toc, titles)
    log('generated table of contents')
    log('not working slugs')
    if not_working_urls == []:
        print('None')
    else:
        print(not_working_urls)
    return


if __name__ == '__main__':
    main()
