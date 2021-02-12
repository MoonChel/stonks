import aiohttp
import asyncio
from lxml import etree

stop_words = [
    "regain",
    "compliance",
    "price",
    "bid",
    "extension",
    "minimum",
    "with",
    "requirement",
    "nasdaq",
    "rule",
    "granted",
    "meet",
    "180-day",
    "group",
    "by",
    "to",
    # nasdaq search api does not recognising companies with "inc." in their names
    "inc.",
]


def replace_new_line(text):
    return text.replace("/n", "")


def get_link_to_article(item):
    return item.cssselect("a.search-result__link")[0].text


def get_article_date(item):
    return item.cssselect("span.search-result__date")[0].text


def remove_stop_words(text: str):
    # add spaces around so we can remove words like " to " without affecting company name
    text = " " + text.lower() + " "

    text = text.replace(",", "")

    for word in stop_words:
        text = text.replace(" " + word + " ", " ")

    return text.strip().title()


async def get_company_ticker(session, company_name):
    ticker_url = "https://api.nasdaq.com/api/autocomplete/slookup/10"

    params = {"search": company_name}

    resp = await session.get(ticker_url, params=params)
    json = await resp.json()

    try:
        symbol = json["data"][0]["symbol"]
    except:
        symbol = None

    return symbol


async def get_tickers():
    url = "https://www.nasdaq.com/api/v1/search?"

    params = {
        "q": "Granted 180-Day Extension",
        "offset": "0",
        "latest": "1",
        "langcode": "en",
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "insomnia/2020.5.2",
    }

    timeout = aiohttp.ClientTimeout(total=5)

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        resp = await session.get(url, params=params)
        json = await resp.json()

        items = []
        for json_item in json["items"]:
            items.append(etree.fromstring(replace_new_line(json_item)))

        dates = [get_article_date(item) for item in items]
        company_names = [remove_stop_words(get_link_to_article(item)) for item in items]
        company_tickers = await asyncio.gather(
            *[
                get_company_ticker(session, company_name)
                for company_name in company_names
            ]
        )

        for date, name, ticker in zip(dates, company_names, company_tickers):
            print(date, name, ticker, sep=" : ")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_tickers())
