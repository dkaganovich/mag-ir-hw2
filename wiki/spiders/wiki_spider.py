# -*- coding: utf-8 -*-
import logging

import scrapy
from scrapy.linkextractors import LinkExtractor

from wiki.items import WikiItem


logger = logging.getLogger(__name__)

class WikiSpider(scrapy.Spider):
    name = "wiki_spider"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = [
        'https://en.wikipedia.org/wiki/IP_address',
        'https://en.wikipedia.org/wiki/Leaves_of_Grass',
        'https://en.wikipedia.org/wiki/Overdraft',
        'https://en.wikipedia.org/wiki/Dark_matter'
    ]

    link_extractor = LinkExtractor(
        allow=(r'/wiki/.+',),
        deny=(r'.*?/wiki/((File|Talk|Category|Portal|Special|Template|Template_talk|Wikipedia|Help|Draft):|Main_Page).*',),
        restrict_xpaths=('//div[@id="mw-content-text"]//p/a[@href and not(starts-with(@href, "#")) and not(contains(@class, "new"))]',),
        tags=('a',)
    )
    title_xpath = 'string(//h1[@id="firstHeading"])'
    snippet_xpath = 'string(//div[@id="mw-content-text"]/p[1])'

    def parse(self, response):
        logger.debug("Parsing: {}".format(response.url))
        # ['url', 'text', 'fragment', 'nofollow']
        outlinks = [response.urljoin(link.url) for link in self.link_extractor.extract_links(response)[:100]]
        logger.debug("Outlinks count ({}): {}".format(response.url, len(outlinks)))

        item = WikiItem()
        item['url'] = response.url
        item['title'] = response.xpath(self.title_xpath).extract_first()
        item['snippet'] = response.xpath(self.snippet_xpath).extract_first()[:255] + "..."
        item['outlinks'] = outlinks
        yield item

        for link in outlinks:
            yield scrapy.Request(link, callback=self.parse)
