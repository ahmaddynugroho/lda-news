# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import re
from calendar import monthrange

import scrapy

DATES = [
    (day+1, month+1, 2022)
    for month in range(11, 12)
    for day in range(0, monthrange(2022, month+1)[1])]


class Detik(scrapy.Spider):
    name = 'detik'
    start_urls = [
        f'https://news.detik.com/indeks/1?date={month:02}/{day:02}/{year}' for day, month, year in DATES]

    def parse(self, response):
        headlines = response.css('h3 a.media__link::text').getall()
        date = response.css('.media__date span::text').get().split(' ')
        for headline in headlines:
            yield {
                'date': f'{date[1]} {date[2]} {date[3]}',
                'headline': headline
            }

        next_links = response.css('.pagination__item')
        for a in next_links:
            if 'Next' in a.get():
                yield response.follow(a, callback=self.parse)


class Kompas(scrapy.Spider):
    name = 'kompas'
    start_urls = [
        f'https://indeks.kompas.com/?site=all&date={year}-{month:02}-{day:02}&page=1' for day, month, year in DATES]

    def parse(self, response):
        headlines = response.css('a.article__link::text').getall()
        headlines_date = response.css('div.article__date::text').getall()
        for headline, date in zip(headlines, headlines_date):
            yield {
                'date': date.split(',')[0],
                'headline': headline
            }

        next_links = response.css('a.paging__link--next')
        for a in next_links:
            if 'Next' in a.get():
                yield response.follow(a, callback=self.parse)


class Okezone(scrapy.Spider):
    name = 'okezone'
    start_urls = [
        f'https://index.okezone.com/bydate/index/{year}/{month:02}/{day:02}/0/' for day, month, year in DATES
    ]

    def parse(self, response):
        TAG_RE = re.compile(r'<[^>]+>')  # delete html tag
        headlines = response.css('h4 a').getall()
        headlines = [TAG_RE.sub('', h).strip() for h in headlines]
        dates = response.css('.f12').getall()
        dates = [TAG_RE.sub('', d).strip().split(
            '|')[1].strip().split(' ') for d in dates]
        dates = [f'{d[1]} {d[2]} {d[3]}' for d in dates]
        for date, headline in zip(dates, headlines):
            yield {
                'date': date,
                'headline': headline
            }

        next_links = response.css('.time a')
        for a in next_links:
            if 'Next' in a.get():
                yield response.follow(a, callback=self.parse)


class Sindonews(scrapy.Spider):
    name = 'sindonews'
    start_urls = [
        f'https://index.sindonews.com/index/0?t={year}-{month:02}-{day:02}' for day, month, year in DATES
    ]

    def parse(self, response):
        TAG_RE = re.compile(r'<[^>]+>')  # delete html tag
        headlines = response.css('.indeks-title a::text').getall()
        dates = response.css('.mini-info ul')
        dates = [
            ' '.join(TAG_RE.sub('', d.get()).split(',')[1].strip().split(' ')[:3]) for d in dates
        ]
        for date, headline in zip(dates, headlines):
            yield {
                'date': date,
                'headline': headline
            }

        next_links = response.css('.pagination a')
        for a in next_links:
            if 'fa-angle-right' in a.get():
                yield response.follow(a, callback=self.parse)


class Tempo(scrapy.Spider):
    name = 'tempo'
    # dates = [(day + 1, 12, 2022) for day in range(0, 3)]
    start_urls = [
        f'https://www.tempo.co/indeks/{year}-{month:02}-{day:02}' for day, month, year in DATES
    ]

    def parse(self, response):
        headlines = response.css('.title a::text').getall()
        headlines = [h.strip() for h in headlines]
        dates = [response.request.url.split('/')[-1]] * len(headlines)
        for date, headline in zip(dates, headlines):
            yield {
                'date': date,
                'headline': headline
            }


class Tribunnews(scrapy.Spider):
    name = 'tribunnews'
    # dates = [(day + 1, 12, 2022) for day in range(0, 3)]
    start_urls = [
        f'https://www.tribunnews.com/index-news/news?date={year}-{month}-{day}&page=1' for day, month, year in DATES
    ]

    def parse(self, response):
        TAG_RE = re.compile(r'<[^>]+>')  # delete html tag
        headlines = response.css('h3 a').getall()
        headlines = [TAG_RE.sub('', h).strip() for h in headlines]
        dates = response.css('time::text').getall()
        dates = [
            ' '.join(d.split(',')[1].strip().split(' ')[:3]) for d in dates]

        # prev_date: prevent double date in one crawl. ex: 30 nov in page 40 of 1 dec crawl
        prev_date = dates[0]
        break_next = False
        for date, headline in zip(dates, headlines):
            if date != prev_date:
                break_next = True
                return
            yield {
                'date': date,
                'headline': headline
            }

        if break_next:
            return
        next_links = response.css('.paging a')
        for a in next_links:
            if 'Next' in a.get():
                yield response.follow(a, callback=self.parse)


# Status: Abandoned
# Reason: Suara only archive news from the last 30 days
class Suara(scrapy.Spider):
    name = 'suara'
    start_urls = [
        # suara doesn't implement per month index
        # manually create page for async advantage
        f'https://www.suara.com/indeks/terkini/all/2022?page={page+1}' for page in range(0, 501)
    ]

    def parse(self, response):
        headlines = [
            h.strip() for h in response.css('.item-inner .post-title a::text').getall()]
        for headline in headlines:
            yield {
                'page': response.request.url.split('=')[-1],
                'headline': headline}

        # using response.follow make the entire proces synchronous
        # next_links = response.css('.pagination a')
        # if next_links:
        #     yield response.follow(next_links[-1], callback=self.parse)
