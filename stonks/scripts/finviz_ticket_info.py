import aiohttp
import asyncio
from lxml import html


async def get_ticker_info():
    url = "https://finviz.com/quote.ashx"
    params = {
        "t": "ITP",
        "ty": "c",
        "p": "d",
        "b": "1",
    }

    selector = "table.snapshot-table2"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "insomnia/2020.5.2",
    }

    timeout = aiohttp.ClientTimeout(total=5)

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        resp = await session.get(url, params=params)
        html_page_text = await resp.text()
        html_page = html.fromstring(html_page_text)
        table = html_page.cssselect(selector)[0]

        attribute_names = table.cssselect("td.snapshot-td2-cp")
        attribute_values = table.cssselect("td.snapshot-td2")

        all_attributes = {
            name.text: value.text_content()
            for name, value in zip(attribute_names, attribute_values)
        }

        print(all_attributes)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_ticker_info())
