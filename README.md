# NewsCrawler

NewsCrawler is a Python-based web scraping tool designed to extract news articles from various sources using multiple techniques. It navigates through paywalls and anti-bot measures to retrieve content, leveraging the Google Cache, Selenium with Stealth Mode, and Archive.is for comprehensive coverage.

## Features

- **Multiple Parsing Methods:** Includes Google Cache, Selenium Stealthed, Archive.is, and direct requests to fetch articles.
- **HTML Validation:** Ensures the integrity of the downloaded content, filtering out insufficient or irrelevant data.
- **Dynamic News Source Handling:** Utilizes a custom `NewsUrlGetter` to dynamically fetch news URLs based on specified topics.
- **Robust Error Handling:** Implements custom exceptions for HTML validation and download errors, ensuring reliability.
- **Extensible Design:** Easily adaptable to include more news sources or parsing methods.

## Dependencies

- Python 3.x
- `requests`
- `selenium`
- `newspaper3k`
- `selenium-stealth`
- `beautifulsoup4`

Ensure you have Chrome WebDriver installed and accessible in your system's PATH for Selenium to function properly.

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourgithubusername/newscrawler.git
```

2. Install the required Python packages:
```sh
pip install -r requirements.txt
```

## Usage

To use NewsCrawler, instantiate the `NewsParser` class with optional parameters for headless browsing and URL filtering. Then, call the `get_news` method with your topic of interest:

```python
from newscrawler import NewsParser, NewsUrlGetter

# Initialize the NewsParser with custom settings
news_parser = NewsParser(NewsUrlGetter(max_results=20, start_date=(2023, 1, 20), end_date=(2023, 12, 25)), headless=True)

# Fetch news articles about "Interest rates"
articles = news_parser.get_news("Interest rates")
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.