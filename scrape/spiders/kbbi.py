import scrapy


class KBBI(scrapy.Spider):
    name = 'kbbi'
    start_urls = ['https://kbbi.kemdikbud.go.id/Account/Login']

    def parse(self, r):
        token = r.xpath('//*[@name="__RequestVerificationToken"]/@value').get()
        formdata = {
            '__RequestVerificationToken': token,
            'Posel': 'rihita3888@breazeim.com',
            'KataSandi': '04012001',
            'IngatSaya': 'false'}
        return scrapy.FormRequest.from_response(
            r, callback=self.parse_index, formdata=formdata)

    def parse_index(self, r):
        for i in range(0, 155):
            yield scrapy.Request(
                f'https://kbbi.kemdikbud.go.id/Cari/Alphabet?masukan=A&masukanLengkap=A&page={i}',
                callback=self.parse_word)

    def parse_word(self, r):
        a = r.css('.col-md-3 a')
        for word_link in a:
            yield r.follow(
                word_link,
                self.parse_rootword,
                meta={'word': word_link.css('a::text').get().strip()}
            )
        # scrapy.shell.inspect_response(r, self)

    def parse_rootword(self, r):
        rootword = r.css('.rootword a::text').get()
        if not rootword:
            rootword = r.meta['word']

        yield {'word': r.meta['word'], 'rootword': rootword}
