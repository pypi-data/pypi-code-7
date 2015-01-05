import re
import sys
import datetime
from calendar import monthrange

import requests

import config as conf

def get_remaining_days():
    today = datetime.date.today()
    end_of_month = datetime.date(today.year,
                                 today.month,
                                 monthrange(today.year,
                                            today.month)[1])
    remaining_days = (end_of_month - today).days
    return remaining_days


def print_current_usage():
    try:
        r = requests.get(conf.USAGE_PAGE_URL)
    except:
        print("Unable to connect to portal.acttv.in")
        sys.exit(1)

    data = r.text

    if not data.strip():
        print("No data in the usage page")
        sys.exit(1)
    search_regex = r'(\d+\.\d+) GB&nbsp;\(Quota&nbsp;(\d+\.\d+)&nbsp;GB\)'
    search_obj = re.search(search_regex, data)

    if search_obj:
        current_usage = float(search_obj.group(1))
        quota = float(search_obj.group(2))
        percent = current_usage / quota * 100
        remaining_days = get_remaining_days()
        print('{} GB of {} GB used ({}%)'.format(current_usage,
                                                 quota,
                                                 percent))
        print('{} days remaining in the current billing cycle'.format(remaining_days))
    else:
        print('Unable to get usage')
        sys.exit(1)

def run():
    print_current_usage()

if __name__ == '__main__':
    run()
