#!/usr/bin/usage python3
# -*- coding: utf-8 -*-
import argparse
import json
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote_plus

def parse_argumnets():
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword", help="keyword to search", nargs=1)
    parser.add_argument("-n",      help="number of search result. default is 5", type=int, default=5, dest="numbers")
    parser.add_argument("-p",      help="page",                                  type=int, default=1, dest="page")
    return parser.parse_args()

def urlfit(url):
    data = json.loads(urlopen('https://developer.url.fit/api/shorten?long_url=' + quote_plus(url)).read().decode())
    return 'https://url.fit/' + data["url"]

def video_like_dislike(link):
    dom = BeautifulSoup(urlopen(link).read().decode(), "html.parser")
    actionable = dom.select('.like-button-renderer')[0]
    like = actionable.select('.like-button-renderer-like-button span')[0].text.strip()
    dislike = actionable.select('.like-button-renderer-dislike-button span')[0].text.strip()
    return "Like: {}, Dislike: {}".format(like, dislike)

def search_youtube(keyword, numbers, page):
    url = 'http://www.youtube.com/results?hl=zh_TW&search_query={}&page={}'.format(quote_plus(keyword), page)
    dom = BeautifulSoup(urlopen(url).read().decode(), "html.parser")

    result = []
    for video in dom.select('.yt-lockup.yt-lockup-tile.yt-lockup-video'):
        link = video.select('.yt-lockup-title a')[0]
        link_text = link.text.strip()
        link_url = 'http://www.youtube.com' + link.get('href').strip()
        description = video.select('.yt-lockup-description')
        description = description[0].text.strip() if description else ''

        result.append("{} ({})".format(link_text, urlfit(link_url)))
        result.append(description)
        result.append(video_like_dislike(link_url))
        result.append("\n")
        numbers -= 1
        if numbers == 0:
            break
    return result

def main():
    args = parse_argumnets()
    print("\n".join(search_youtube(args.keyword[0], args.numbers, args.page))[0:-2])

if __name__ == '__main__':
    main()
