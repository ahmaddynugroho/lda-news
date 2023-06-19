import scrapy


class lemmatize(scrapy.Spider):
    name = 'lemmatize'
    headlines = [
        # 'pemrograman pemrosesan program polda'
        'Polda Metro Terima Pemberitahuan Reuni 212 di Masjid At-Tin TMII Besok',
        'Rayakan Timnas Kalah di Piala Dunia Berujung Pria Iran Meregang Nyawa'
    ]
    headlines = [h.split(' ') for h in headlines]
    start_urls = [
        f'https://kbbi.kemdikbud.go.id/entri/{h[0]}?next=' + ','.join(h[1:]) for h in headlines
    ]

    def parse(self, response):
        next_words = response.request.url.split('=')
        if not next_words[1]:
            meta = self.get_rootword(response)
            yield {'processed_h': ' '.join(meta['pw'])}
            return
        next_words = next_words[1].split(',')

        meta = self.get_rootword(response)

        next_url = f'https://kbbi.kemdikbud.go.id/entri/{next_words.pop(0)}?next=' + ','.join(
            next_words)
        yield scrapy.Request(next_url, self.parse, meta=meta)

    def get_rootword(self, response):
        rootword = response.css('.rootword a::text').get()
        if not rootword:
            url = response.request.url
            rootword = url.split('entri/')[1].split('?')[0]

        meta = response.meta
        if not 'pw' in meta:
            meta['pw'] = []
        meta['pw'].append(rootword)
        return meta
