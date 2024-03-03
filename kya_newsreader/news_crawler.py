import time
from typing import List
from newspaper import ArticleException, Article
import newspaper
from selenium_stealth import stealth
from selenium import webdriver
from news_url_getter import NewsUrlGetter
import constant
from bs4 import BeautifulSoup
from logging import getLogger
from dataclasses import dataclass
from enum import Enum
from exceptions import HTMLValidationException, HTMLDownloadException

logger = getLogger(__name__)

class ParsingMethod(Enum):
    GOOGLE_CACHE = 1
    SELENIUM_STEALTHED = 2
    ARCHIVE = 3
    REQUEST = 4
    

@dataclass
class HtmlWithMethod:
    html: str
    parsing_method: ParsingMethod

class NewsParser:
    def create_driver_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")

        if self.headless_driver:
            options.add_argument("--headless")

        # options.add_argument("--disable-gpu");
        # options.add_argument("--disable-crash-reporter");
        # options.add_argument("--disable-extensions");
        options.add_argument("--disable-in-process-stack-traces")
        options.add_extension('kya_newsreader/paywall_ext.crx')
        options.add_argument("--disable-logging")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--logger-level=3")
        options.add_argument("--output=/dev/null")
        options.add_argument("--disable-images")
        options.page_load_strategy = 'eager'
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options
    
    @staticmethod
    def create_driver(options):
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)
        driver.set_script_timeout(15)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        
        return driver
    
    def __init__(self, url_getter=None, headless=False):
        """
        Initializes a NewsCrawler object.

        :param url_getter: An instance of NewsUrlGetter or implementing get_news_url(topic: str, follow_redirect=True) -> List[str]
        :return: None
        """
        self.url_getter = url_getter
        if self.url_getter is None:
            self.url_getter = NewsUrlGetter(max_results=5)
        
        self.headless_driver = headless
        self.options = self.create_driver_options()
        self.parsing_statistics = None
    
    def validate_html(self, html: str, url: str) -> bool:
        """
        Validate the html of an article
        :param html: The html to validate
        :return: True if the html is valid, False otherwise
        """
        if html is None or len(html) < 400:
            raise HTMLValidationException("Parse HTML is null")
        
        article = Article(url)
        article.download(html)

        # Formatted this way to know that there can be an issue during download
        try:
            article.parse()
        except ArticleException as e:
            raise e
        
        article_text = article.text.strip() + article.title

        if len(article.text) < 120\
            or "Partner content: This content" in article_text \
            or "Error 404" in article_text\
            or "security service to protect itself from online attacks" in article_text\
            or "understand that not everyone can afford to pay for expensive news subscriptions" in article_text\
            or "products or services. Here is a list of our partners" in article_text:
            raise HTMLValidationException("Parsed content too short or not found")
        
        lower = html.lower().strip()
        # if "enable javascript" in lower or "supports javascript" in lower:
        #     raise HTMLValidationException("Javascript not supported")
        
        if "we suspect you are using an automated system" in lower or "bad bot" in lower:
            raise HTMLValidationException("Crawlers not supported by website")
        
        if "Our engineers are working quickly to resolve the issue.".lower() in lower:
            raise HTMLValidationException("Website down")
        
        
        return True

    def try_populate_html(self, url: str) -> HtmlWithMethod:
        """
        Try to populate the html of a url
        :param url: The url to populate
        :return: The html of the url
        """

        logger.info("Instantiating a driver")
        driver = self.create_driver(self.options)
        logger.info("Trying to get HTML with parsing method: " + str(ParsingMethod.GOOGLE_CACHE))
        try:
            html = self.download_article_with_google_cache(url, driver)
            valid = self.validate_html(html, url)
            assert valid
            return HtmlWithMethod(html, ParsingMethod.GOOGLE_CACHE)

        except HTMLDownloadException as e:
            logger.warn(e)
        except HTMLValidationException as e:
            logger.warn("Failed to validate HTML: " + str(e))


        logger.info("Trying to get HTML with parsing method: " + str(ParsingMethod.SELENIUM_STEALTHED))
        try:
            driver.get(url)
            time.sleep(3)
            html = driver.page_source
            valid = self.validate_html(html, url)
            assert valid
            return HtmlWithMethod(html, ParsingMethod.SELENIUM_STEALTHED)
        
        except HTMLDownloadException as e:
            logger.warn(e)
        except HTMLValidationException as e:
            logger.warn("Failed to validate HTML: " + str(e))


        logger.info("Trying to get HTML with parsing method: " + str(ParsingMethod.ARCHIVE))
        try:
            html = self.download_article_with_archive_is(url, driver)
            valid = self.validate_html(html, url)
            assert valid
            return HtmlWithMethod(html, ParsingMethod.ARCHIVE)
            
        except HTMLDownloadException as e:
            logger.warn(e)
        except HTMLValidationException as e:
            logger.warn("Failed to validate HTML: " + str(e))

        

    def download_article_with_google_cache(self, url: str, driver: webdriver.Chrome) -> str:
        """
        Download an article using google cache
        :param url: The url of the article
        :return: The article text
        """
        try:
            driver.get(constant.GOOGLE_CACHE + url)
            return driver.page_source
        except Exception as e:
            raise HTMLDownloadException(f"Error getting {url} google cache: {e}")
            
            
    def download_article_with_archive_is(self, url: str, driver) -> str:
        """
        Download an article using archive.is
        :param url: The url of the article
        :return: The article text
        """
        try:
            driver.get("https://archive.is/"+url)
        except Exception as e:
            raise HTMLDownloadException(f"Error reaching archive.is: {e}")
        
        response = driver.page_source
        soup = BeautifulSoup(response, 'html.parser')

        try:
            # Find the first link within `TEXT-BLOCK` class
            link = soup.find("div", class_="TEXT-BLOCK").find("a")['href']
        except Exception as e:
            raise HTMLDownloadException(f"Error parsing {url} archive.is: {str(e)}")

        driver.get(link)
        return driver.page_source

    def get_news(self, topic: str) -> List[Article]:
        """
        Get news articles from Google News
        Uses multiple techniques such as google cache and archive.is to get the article text
        :param topic: The topic to search for
        :return: A list of dictionaries containing news articles
        """
        urls = self.url_getter.get_news_url(topic)
        logger.info(f"Got {len(urls)} urls")

        articles: List[Article] = []
        parsing_statistics = {
            'failed': [],
            str(ParsingMethod.ARCHIVE): [],
            str(ParsingMethod.GOOGLE_CACHE): [],
            str(ParsingMethod.REQUEST): [],
            str(ParsingMethod.SELENIUM_STEALTHED): []
        }
        for urlAndHtml in urls:
            logger.info("Trying to parse url: " + urlAndHtml.url)
            try:
                self.validate_html(urlAndHtml.html, urlAndHtml.url)
                valid = True
            except HTMLValidationException as e:
                logger.warn("Provided HTML is not valid:", exc_info=e, stack_info=False)
                valid = False

            if not valid:
                htmlWithMethod = self.try_populate_html(urlAndHtml.url)
                if htmlWithMethod is None:
                    parsing_statistics['failed'].append(urlAndHtml.url)
                    continue

            else:
                htmlWithMethod = HtmlWithMethod(urlAndHtml.html, ParsingMethod.REQUEST)

            parsing_statistics[str(htmlWithMethod.parsing_method)].append(urlAndHtml.url)
            logger.info("Article download succeeded with method: " + str(htmlWithMethod.parsing_method))
            article = newspaper.Article(urlAndHtml.url)

            article.download(htmlWithMethod.html)
            article.parse()
            articles.append(article)
            
        self.parsing_statistics = parsing_statistics
        return articles

if __name__ == "__main__":
    np = NewsParser(NewsUrlGetter(max_results=20, start_date=(2023, 1, 20), end_date=(2023, 12, 25)))
    articles = np.get_news("Interest rates")