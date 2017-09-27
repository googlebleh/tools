#!/usr/bin/python3

import collections
import os
import re
import shutil
import urllib.request
from bs4 import BeautifulSoup

#  https://video.fagc2-1.fna.fbcdn.net/v/t42.3356-2/18286498_1454375877916407_6550172108217909248_n.mp4/video-1493844829.mp4?vabr=428952&oh=8a45c438b2a3c47332f891434c64adb1&oe=590C9ED1&dl=1
#  https://scontent.fagc2-1.fna.fbcdn.net/v/t15.3394-10/18324344_1454375874583074_4713998126602518528_n.jpg?oh=d83c8f69989d64f2d6330a7633be287f&oe=597E9175
fname_regex = re.compile(r'\w+\.(jpg|jpeg|png|bmp|gif|mp4)', re.I)


def dl_from_a_tag(tag):
    viewing_url = tag['href']
    dl_url = viewing_url + '&dl=1'

    m = fname_regex.search(dl_url)
    if m:
        fname = m.group(0)
        new_name, ext = os.path.splitext(fname)
        n = 1
        while os.path.isfile(fname):
            fname = new_name + '_' + str(n) + ext
            n += 1

        # http://stackoverflow.com/a/7244263/6466133
        with urllib.request.urlopen(dl_url) as response, open(fname, 'wb') as f:
            shutil.copyfileobj(response, f)
        print(fname)

    else:
        print('skip:', dl_url)


soup = BeautifulSoup(input(''), 'html.parser')
tags = soup.find_all('a')
jobs = map(dl_from_a_tag, tags)
collections.deque(jobs, maxlen=None)
