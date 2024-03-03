from setuptools import setup, find_packages

setup(
    name='NewsCrawler',
    version='1.0.0',
    author='Kya',
    description='A Python-based tool for scraping news articles from various sources, using different techniques.',
    long_description=open('README.md').read(),
    long_description_content_type='A Python-based tool for scraping news articles from various sources, using different techniques.',
    url='https://github.com/yourgithubusername/newscrawler',
    packages=find_packages(),
    keywords='news, web scraping, article scraping, news scraping',
    install_requires=[
        'requests',
        'selenium',
        'newspaper3k',
        'selenium-stealth',
        'beautifulsoup4',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)