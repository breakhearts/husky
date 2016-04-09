"""
Yahoo stock api
"""
from datetime import datetime, timedelta


def get_history_data_url(stock, start=None, end=None):
    """
    >>> get_history_data_url("BIDU", start="20150213", end="20150914")
    'http://real-chart.finance.yahoo.com/table.csv?s=BIDU&g=d&ignore=.csv&a=1&b=14&c=2015&d=8&e=14&f=2015'
    """
    query = "?s={0}&g=d&ignore=.csv".format(stock)
    if start:
        start_date = datetime.strptime(start, "%Y%m%d") + timedelta(days=1)
        query += "&a={0}&b={1}&c={2}".format(start_date.month - 1, start_date.day, start_date.year)
    if end:
        end_date = datetime.strptime(end, "%Y%m%d")
        query += "&d={0}&e={1}&f={2}".format(end_date.month - 1, end_date.day, end_date.year)
    api = "http://real-chart.finance.yahoo.com/table.csv" + query
    return api


def parse_history_data(content):
    data = []
    for line in content.splitlines()[1:]:
        t = line.split(",")
        if len(t) == 7:
            data.append(t)
    return data


def headlines_url(stock):
    api = "http://finance.yahoo.com/q/h?s={0}+Headlines".format(stock)
    return api


def press_releases(stock):
    api = "http://finance.yahoo.com/q/p?s={0}+Press+Releases".format(stock)
    return api


def company_event(stock):
    api = "http://finance.yahoo.com/q/ce?s={0}+Company+Events".format(stock)
    return api

if __name__ == "__main__":
    import doctest
    doctest.testmod()