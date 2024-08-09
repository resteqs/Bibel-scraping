import scrapy
import re
#POLNCV has 693 lines
class BibleSpider(scrapy.Spider):
    name = "holyjesus"

    def start_requests(self):
        yield scrapy.Request(url=f"https://live.bible.is/bible/POLNCV/MAT/1", callback=self.parse_chapter)

    def parse_chapter(self, response):
        js = response.css("script::text").get()
        pattern = re.compile(r'"([A-Z0-9]+)"(?=:"(?:OT|NT)")')  # Only books from new testament
        booknames = pattern.findall(js)
        booknames = list(dict.fromkeys(booknames))
        self.log(f'Extracted chapter names: {booknames}')
        
        for book in booknames:
            url = f'https://live.bible.is/bible/POLNCV/{book}/1?audio_type=audio_drama'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        verses = response.xpath('//div[@class="chapter justify"]//span[contains(@class, "align-left") and @data-verseid]')
        bible = response.xpath('//h1[@class="version-text"]/text()').get()
        book = response.url.split('/')[5]
        chapter = response.url.split('/')[6].split('?')[0]
        language = response.url.split('/')[4]
        counter = 0
        for verse in verses:
            counter = counter + 1
            verse_number = verse.xpath('@data-verseid').get()
            verse_text = verse.xpath('.//span/text()').get(default="not-found")

            yield {
                'language': language,
                'bible': bible,
                'book': book,
                'chapter': chapter,
                'verse_number': verse_number,
                'verse_text': verse_text,
            }
        if counter != 0:
            new_chapter = int(chapter) + 1
            next_page_url = f'https://live.bible.is/bible/POLNCV/{book}/{new_chapter}?audio_type=audio_drama'
            yield scrapy.Request(next_page_url, callback=self.parse)
