import bs4
import scrapy
from scrapy.loader import ItemLoader

from sweep.items import HcpreportsItem
from sweep.utils import get_string, derive_date_from_age, derive_date_from_cin
from sweep.settings import START, STOP, STEP, SECONDARY_START, SECONDARY_STOP, SECONDARY_STEP


class HcreportsSpider(scrapy.Spider):
    name = "hcpreports"
    allowed_domains = ["hcpreports.blogspot.in"]

    def start_requests(self):
        for year in range(START, STOP, STEP):
            for month in range(SECONDARY_START, SECONDARY_STOP, SECONDARY_STEP):
                url = "http://hcpreports.blogspot.in/{0}/{1:0>2}/".format(year, month)
                yield scrapy.Request(url, self.parse)

    def parse(self, response):
        status = True
        if response.status == 404:
            # Skip this page
            status = False
        if response.xpath("//div/@class[contains(., 'status-msg-body')]").extract():
            # Skip this page
            status = False
        if len(response.xpath("//div/@class[contains(., 'date-outer')]").extract()) > 1:
            # Skip this page if there are multiple date outer
            status = False
        if status:
            # response.xpath("//div/@id[contains(., 'PopularPosts1')]").extract()
            batch_list = []
            batch_list += response.xpath("//a/@href[contains(., '/batch')]").extract()
            batch_list += response.xpath("//a/@href[contains(., '/indian-films-star')]").extract()
            batch_list += response.xpath("//a/@href[contains(., '/female-artistes')]").extract()
            batch_list += response.xpath("//a/@href[contains(., '/directors')]").extract()
            batch_list += response.xpath("//a/@href[contains(., '/database-of-indian-music-directors')]").extract()
            selected = list(set(batch_list))
            for sel in selected:
                if '#' in sel or len(sel.split('/')) != 6:
                    continue
                url = str(sel).strip()
                yield scrapy.Request(url, callback=self.hcpreports_parse)

    def hcpreports_parse(self, response):
        status = True
        if response.status == 404:
            # Skip this page
            status = False
        if response.xpath("//div/@class[contains(., 'status-msg-body')]").extract():
            # Skip this page
            status = False
        if len(response.xpath("//div/@class[contains(., 'date-outer')]").extract()) > 1:
            # Skip this page if there are multiple date outer
            status = False
        if status:
            soup = bs4.BeautifulSoup(get_string(response.body), "lxml")
            url = [str(response.url).strip()]
            today = ["today"]
            batch = None
            if soup.h3 and 'BATCH' in soup.h3.text:
                batch = self.batch_details_parse(batch=soup.h3.text, is_url=False)
            else:
                batch = self.batch_details_parse(batch=str(response.url).strip(), is_url=True)
            gender = self.gender_parse(str(str(response.url).strip().split('/')[-1]).split('.')[0])
            category = self.category_parse(str(str(response.url).strip().split('/')[-1]).split('.')[0])
            rows = soup.findAll('td')
            for row in rows:
                info_dict = self.contact_details_parse(row.text.encode('utf-8').strip())
                if not info_dict:
                    continue
                loader = ItemLoader(item=HcpreportsItem())
                loader.add_value("url", url)
                loader.add_value("created", today)
                loader.add_value("updated", today)
                loader.add_value("batch", batch)
                loader.add_value("name", info_dict.get("name").decode('utf-8'))
                loader.add_value("email", info_dict.get("email").decode('utf-8'))
                loader.add_value("gender", gender)
                loader.add_value("type", category)
                yield loader.load_item()

    def batch_details_parse(self, batch, is_url=False):
        return batch.split(' ')[1] if not is_url else (batch.split('/')[-1]).split('.html')[0]

    def contact_details_parse(self, text):
        response = {}
        if text:
            info = text.split(' <')
            if len(info) == 2 and '@' in info[1]:
                response = {'name': info[0], 'email': str(info[1]).replace('>', '')}
            elif '@' in info[0]:
                response = {'name': str(info[0]).split('@')[0], 'email': info[0]}
            else:
                pass
        return response

    def gender_parse(self, text):
        categories = {
            'indian-films-star': 'male',
            'female-artistes_12': 'female'
        }
        return categories[text] if text in categories else 'unknown'

    def category_parse(self, text):
        categories = {
            'indian-films-star': 'actor',
            'female-artistes_12': 'actress',
            'directors': 'director',
            'database-of-indian-music-directors': 'music director'
        }
        return categories[text] if text in categories else 'general'
