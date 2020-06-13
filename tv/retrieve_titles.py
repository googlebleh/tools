#!/usr/bin/env python3

import sys, os, time
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from titlecase import titlecase
# TODO: import functools (lru_cache), doctest, unittest

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
    
    def __repr__(self):
        return "{}(show_name={!r}, use_cache={!r})".format(self.__class__.__name__,
                                                           self.show_name,
                                                           self.use_cache)
    
    def __str__(self):
        return self.epslist_pageid
    
    def __hash__(self):
        return hash(self.epslist_pageid)
    
    def __eq__(self, other):
        return (self.epslist_pageid == other.epslist_pageid)
    
    def __lt__(self, other):
        return (self.epslist_pageid < other.epslist_pageid)
    
    def get_epslist_page(self):
        hdr = {
            "User-Agent" : "Mozilla/5.0",
            "Accept"     : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        try:
            epslist_req = urllib.request.Request(self.epslist_url, headers=hdr)
            with urllib.request.urlopen(epslist_req) as page:
                return page.read()
            
        except urllib.error.HTTPError as E:
            print("Error code {} while accessing\n  {}".format(E.code, self.epslist_url))
            man_url = input("Please enter a different URL --> ")
            if (man_url == ""): sys.exit(os.EX_NOINPUT)
            
            epslist_req = urllib.request.Request(man_url, headers=hdr)
            with urllib.request.urlopen(epslist_req) as page:
                self.epslist_url = man_url
                return page.read() # after updating self.epslist_url
            
    def order_soup(self):
        if ((self.epslist_pageid in WikiShowLookup.cached_soup) and self.use_cache):
            self.epslist_soup = WikiShowLookup.cached_soup[self.epslist_pageid]
        else:
            self.epslist_soup = BeautifulSoup(self.get_epslist_page(), "html.parser")
            WikiShowLookup.cached_soup[self.epslist_pageid] = self.epslist_soup
    
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
        
        episode_row = season_table.find_all("tr", {"class":"vevent"})[int(episode) - 1]
        title_cell = episode_row.find("td", {"class":"summary"})
        
        cell_text = title_cell.get_text()
        m = re.search(r'"(.+)"', cell_text)
        return m.group(1) if m else cell_text

# try to episode_title_lookup(*m.groups()[:3])
def episode_title_lookup(show_name, season_num, episode_num):
    return WikiShowLookup(show_name).episode_title(season_num, episode_num)

def unittest_eps_title_lu(show, season, eps, expected):
    print(' '*4, "{} S{:02}E{:02}:".format(titlecase(show), season, eps), end=' ')
    retval = episode_title_lookup(show, season, eps)
    print(retval.encode('utf-8'))
    assert(retval == expected)

def test_eps_title_lu():
    print(' '*2, "Testing episode_title_lookup()...")
    start = time.clock()
    
    unittest_eps_title_lu("adventure time", 6, 13, "Thanks for the Crabapples, Giuseppe!")
    unittest_eps_title_lu("adventure time", 5, 52, "Billy's Bucket List")
    
    print(' '*4, "The Legend of Korra S02E08:", end=' ')
    r = episode_title_lookup("the legend of korra", "two", 8)
    print(r)
    assert(r == "Beginnings, Part 2")
    
    # unittest_eps_title_lu("adventure time", 5, 51, "Lemonhope (Part 1)")
    # unittest_eps_title_lu("gintama", 1, 4, "Watch Out! Weekly Shonen JUMP Sometimes Comes Out On Saturdays!")
    
    # Demoing the cache
    unittest_eps_title_lu("silicon valley", 2, 9, "Binding Arbitration")
    unittest_eps_title_lu("the big bang theory", 5, 21, "The Hawking Excitation")
    unittest_eps_title_lu("archer", 2, 11, "Jeu Monégasque")
    
    unittest_eps_title_lu("archer", 3, 1, "Heart of Archness: Part I")
    unittest_eps_title_lu("the big bang theory", 6, 9, "The Parking Spot Escalation")
    unittest_eps_title_lu("silicon valley", 2, 10, "Two Days of the Condor")
    unittest_eps_title_lu("the big bang theory", 4, 8, "The 21-Second Excitation")
    # unittest_eps_title_lu("the big bang theory", 2, 6, "The Cooper-Nowitzki Theorem")
    unittest_eps_title_lu("the big bang theory", 2, 6, "The Cooper–Nowitzki Theorem")
    unittest_eps_title_lu("archer", 5, 13, "Archer Vice: Arrival/Departure")
    unittest_eps_title_lu("archer", 3, 13, "Space Race: Part II")
    unittest_eps_title_lu("silicon valley", 1, 7, "Proof of Concept")
    unittest_eps_title_lu("archer", 3, 3, "Heart of Archness: Part III")
    unittest_eps_title_lu("the big bang theory", 8, 24, "The Commitment Determination")
    unittest_eps_title_lu("archer", 3, 12, "Space Race: Part I")
    unittest_eps_title_lu("archer", 3, 2, "Heart of Archness: Part II")
    
    elapsed = time.clock() - start
    print(' '*2, "Passed in {:.3f} seconds".format(elapsed))

def runtests():
    print("Testing...")
    test_eps_title_lu()
    print("All tests passed")

def main():
    runtests()
    return 0

if __name__ == "__main__":
    main()
