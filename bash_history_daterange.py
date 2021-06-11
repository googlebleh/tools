#!/usr/bin/env python3

import datetime
import fileinput
import re


start_date = datetime.datetime(2021, month=1, day=29, hour=14)
end_date = datetime.datetime(2021, month=1, day=30)

date_regex = re.compile(r"#(\d+)$", re.MULTILINE)

cmd_date = None
for line in fileinput.input():
    m = date_regex.match(line)
    if m:
        cur_date = int(m.group(1))
        cmd_date = datetime.datetime.fromtimestamp(cur_date)

    elif start_date < cmd_date < end_date:
        print(cmd_date.strftime("%y%m%d"), line.strip())
