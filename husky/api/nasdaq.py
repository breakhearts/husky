from lxml import etree
import requests
from husky.utils import utility

REAL_TIME_QUOTE = 1
AFTER_HOUR_QUOTE = 2
PRE_MARKET_QUOTE = 3


def real_time_quote_slice_url(code, time, page):
    return "http://www.nasdaq.com/symbol/%s/time-sales?time=%d&pageno=%d"%(code, time, page)

def pre_market_quote_slice_url(code, time, page):
    return "http://www.nasdaq.com/zh/symbol/%s/premarket?time=%d&page=%d"%(code, time, page)

def after_hour_quote_slice_url(code, time, page):
    return "http://www.nasdaq.com/zh/symbol/%s/after-hours?time=%d&page=%d"%(code, time, page)

def quote_slice_url_by_type(type, code, time, page):
    if type == REAL_TIME_QUOTE:
        return real_time_quote_slice_url(code, time, page)
    elif type == AFTER_HOUR_QUOTE:
        return after_hour_quote_slice_url(code, time, page)
    elif type == PRE_MARKET_QUOTE:
        return pre_market_quote_slice_url(code, time, page)

def short_interest_url(code):
    return "http://www.nasdaq.com/symbol/%s/short-interest" % code

def options_url(code, page):
    return "http://www.nasdaq.com/symbol/%s/option-chain?dateindex=-1&page=%d"%(code, page)

def normalize_date(data):
    try:
        return normalize_date_v1(data)
    except:
        try:
            return normalize_date_v2(data)
        except:
            return normalize_date_v3(data)

def normalize_date_v1(data):
    m_map = {
        "Jan" : 1,
        "Feb" : 2,
        "Mar" : 3,
        "Apr" : 4,
        "May" : 5,
        "Jun" : 6,
        "Jul" : 7,
        "Aug" : 8,
        "Sep" : 9,
        "Oct" : 10,
        "Nov" : 11,
        "Dec" : 12
    }
    month, p = data.split(".")
    month = m_map[month]
    day, year = p.split(",")
    year = year.strip()
    year = int(year[:-2])
    day = int(day)
    return "%d-%02d-%02d"%(year, month, day)

def normalize_date_v2(data):
    from datetime import datetime
    t = datetime.strptime(data, "%m/%d/%Y %H:%M")
    return t.strftime("%Y-%m-%d")

def normalize_date_v3(data):
    m_map = {
        "Jan" : 1,
        "Feb" : 2,
        "Mar" : 3,
        "Apr" : 4,
        "May" : 5,
        "Jun" : 6,
        "Jul" : 7,
        "Aug" : 8,
        "Sep" : 9,
        "Oct" : 10,
        "Nov" : 11,
        "Dec" : 12
    }
    month = data[:3]
    p = data[3:]
    month = m_map[month]
    day, year = p.split(",")
    year = int(year)
    day = int(day)
    return "%d-%02d-%02d"%(year, month, day)

def normalize_price(data):
    price = data.encode("utf-8")
    return price[3:-3]

REAL_TIME_QUOTE_TIME_SLICE_MAX = 13
AFTER_HOUR_QUOTE_TIME_SLICE_MAX = 8
PRE_MARKET_QUOTE_TIME_SLICE_MAX = 11

def get_time_slice_max(type):
    if type == REAL_TIME_QUOTE:
        return REAL_TIME_QUOTE_TIME_SLICE_MAX
    elif type == AFTER_HOUR_QUOTE:
        return AFTER_HOUR_QUOTE_TIME_SLICE_MAX
    elif type == PRE_MARKET_QUOTE:
        return PRE_MARKET_QUOTE_TIME_SLICE_MAX
    else:
        return None

class NoTradingDataException(Exception):
    pass

class ParseException(Exception):
    pass

def parse_time_quote_slice_page(content):
    assert content.find("http://www.nasdaq.com") != -1
    tree = etree.HTML(content)
    symbol = tree.xpath('//form[@id="stock-search"]')
    assert symbol
    gb =  tree.xpath('//div[@class="green-box"]/text()')
    if gb and gb[0].find("This symbol is not recognized.") != -1:
        raise NoTradingDataException
    nipo = tree.xpath('//div[@class="notTradingIPO"]')
    if nipo:
        raise NoTradingDataException
    #check page correct
    markettime_tag = tree.xpath('//*[@id="qwidget_markettime"]')
    if not markettime_tag:
        raise NoTradingDataException
    try:
        date = tree.xpath('//*[@id="qwidget_markettime"]/text()')[0].encode("utf-8").strip()
    except:
        raise NoTradingDataException
    date = normalize_date(date)
    data = []
    for t in tree.xpath('//table[@id="AfterHoursPagingContents_Table"]/tr | //table[@id="AfterHoursPagingContents_Table"]/tbody/tr'):
        tr = t.xpath("td/text()")
        time = tr[0]
        price = normalize_price(tr[1])
        volume = tr[2]
        data.append((time, price, volume))
    t = tree.xpath('//ul[@class="pager"]/li/*')
    if len(t) == 0:
        first = 1
        last = 1
        current = 1
    else:
        #first = t[0].xpath("@href")
        current = int(t[2].xpath('text()')[0])
        first = 1
        last = t[-1].xpath("@href")
        if len(last) == 0:
            last = current
        else:
            last = int(last[0].split("=")[-1])
    return date, data, current, first, last


def get_company_list(exchange, timeout):
    api = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange={0}&render=download".format(exchange)
    r = requests.get(api, headers={"user-agent": utility.random_ua()}, timeout=timeout)
    if r.status_code == 200:
        data = []
        for line in r.content.splitlines()[1:]:
            t = [x.strip('"') for x in line.split('",')]
            symbol, name, last_sale, market_cap, adr_tso, ipo_year, sector, industry, summary_quote = t[:9]
            market_cap = int(float(market_cap))
            data.append((symbol, name, market_cap))
        return data
    else:
        return None


def get_nasdaq_company_list():
    return get_company_list("NASDAQ", timeout =10)


def get_nyse_company_list():
    return get_company_list("NYSE", timeout =10)


def get_amex_company_list():
    return get_company_list("AMEX", timeout =10)


def get_all_company_list():
    company_list = get_nasdaq_company_list()
    company_list += get_nyse_company_list()
    company_list += get_amex_company_list()
    t = []
    symbols = {}
    for symbol, name, market_cap in company_list:
        if not symbol.isalpha():
            continue
        if symbol not in symbols:
            symbols[symbol] = True
            t.append((symbol, name, market_cap))
    t.sort(cmp=lambda x,y : cmp(x[2] ,y[2]),reverse=True)
    return t