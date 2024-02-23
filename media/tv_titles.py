#!/usr/bin/env python3

import re
import urllib.error
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup
from titlecase import titlecase


class WikiShowLookup:
    cached_soup = dict()
    wiki_article_url_base = "http://en.wikipedia.org/wiki/"

    def __init__(self, show_name, use_cache=True):
        self.show_name = titlecase(show_name)
        self.use_cache = use_cache

        escaped = urllib.parse.quote(self.show_name.replace(' ', '_'))
        self.epslist_pageid = "List_of_{}_episodes".format(escaped)
        self.epslist_url = WikiShowLookup.wiki_article_url_base + self.epslist_pageid
        self.order_soup()

    def get_epslist_page(self):
        hdr = {
            "User-Agent" : "Mozilla/5.0",
            "Accept"     : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        epslist_req = urllib.request.Request(self.epslist_url, headers=hdr)
        with urllib.request.urlopen(epslist_req) as page:
            return page.read()

    def order_soup(self):
        if self.use_cache:
            if self.epslist_pageid in WikiShowLookup.cached_soup:
                self.epslist_soup = WikiShowLookup.cached_soup[self.epslist_pageid]
                return

        self.epslist_soup = BeautifulSoup(self.get_epslist_page(), "html.parser")

    def episode_title(self, season, episode):
        header_attrs = {
            "class" : "mw-headline",
            "id"    : re.compile(r"(Season|Series|Book)_{}".format(season), re.IGNORECASE)
        }
        # maybe todo: some shows only have one season, so there's no season_header
        # gintama season 1 eps 4, s07e04 breaks it (maybe not anymore now that we have get_text)
        # add support for part1 part2
        # also instead of indexing through the list to get row, maybe you can TRY A LITTLE HARDER
        season_header = self.epslist_soup.find("span", header_attrs)
        season_table = season_header.find_next("table")

        episode_row = season_table.find_all("tr", {"class":"vevent"})[int(episode)-1]
        title_cell = episode_row.find("td", {"class":"summary"})

        cell_text = title_cell.get_text()
        m = re.search(r'"(.+)"', cell_text)
        return m.group(1) if m else cell_text


# try to get_episode_title(*m.groups()[:3])
def get_episode_title(show_name, season_num, episode_num):
    return WikiShowLookup(show_name).episode_title(season_num, episode_num)
