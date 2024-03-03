import requests
from dataclasses import dataclass
from typing import List
from gnews import GNews
from urllib.parse import urlparse, urljoin

@dataclass
class NewsUrl:
    url: str
    html: str


class NewsUrlGetter(GNews):
    def __init__(self, language="en", country="US", max_results=100, start_date=None, end_date=None,
                 exclude_websites=None, proxy=None):
        """
        (optional parameters)
        :param language: The language in which to return results, defaults to en (optional)
        :param country: The country code of the country you want to get headlines for, defaults to US
        :param max_results: The maximum number of results to return. The default is 100, defaults to 100
        :param period: The period of time from which you want the news
        :param start_date: Date after which results must have been published
        :param end_date: Date before which results must have been published
        :param exclude_websites: A list of strings that indicate websites to exclude from results
        :param proxy: The proxy parameter is a dictionary with a single key-value pair. The key is the
        protocol name and the value is the proxy address
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Referer': 'https://www.google.com/'
        }

        super().__init__(language=language, country=country, start_date=start_date, end_date=end_date, max_results=max_results, exclude_websites=exclude_websites, proxy=proxy)

    @staticmethod
    def clean_url(url: str) -> str:
        """
        Clean a URL
        :param url: The URL to clean
        :return: The cleaned URL
        """

        return urljoin(url, urlparse(url).path)

    def get_news_url(self, topic: str, timeout=2) -> List[NewsUrl]:
        """
        Get news articles from Google News
        :param topic: The topic to search for
        :return: A list of dictionaries containing news articles
        """
        news = self.get_news(topic)
        urls = [article['url'] for article in news]

        extracted_urls = []

        for url in urls:
            try:
                r = requests.get(url, timeout=timeout, headers=self.headers)
                if r.history and len(self.clean_url(r.url)) < 45:
                    print([u.url for u in r.history])
                    r = r.history[-1]
                extracted_urls.append(NewsUrl(self.clean_url(r.url), r.text))
                continue
            except requests.exceptions.RequestException as e:
                pass

            try: extracted_urls.append(NewsUrl(self.clean_url(r.url), None))
            except UnboundLocalError as e: pass

        return extracted_urls