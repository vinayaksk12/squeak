import bs4
import scrapy
from scrapy.loader import ItemLoader

from sweep.items import CompanyItem
from sweep.utils import get_string, derive_date_from_age, derive_date_from_cin
from sweep.settings import START, STOP, STEP


"""
scrapy crawl zaubacorp -o items.json
"""

company_keys = {
    "cin": "cin", "llp_identification_number": "cin", "foreign_company_registration_number": "cin",
    "company_name": "name", "roc": "roc", "country_of_incorporation": "roc",
    "company_category": "category", "type_of_office": "category",
    "main_division_of_business_activity_to_be_carried_out_in_india": "category",
    "sub_category": "sub_category", "description_of_main_division": "sub_category", "company_sub_category": "sub_category",
    "registration_number": "registration_number", "class_of_company": "company_class",
    "date_of_incorporation": "incorporation_date", "email_id": "email", "website": "website",
    "address": "address", "number_of_members": "member_count", "activity": "activity",
    "company_status": "status", "url": "url"
}


class ZaubacorpSpider(scrapy.Spider):
    name = "zaubacorp"
    allowed_domains = ["www.zaubacorp.com"]
    # start_urls = ["https://www.zaubacorp.com/company-list/p-1-company.html",
    #               "https://www.zaubacorp.com/company/-ART-FACTORY-PRIVATE-LIMITED/U92142KL1996PTC010396"]

    def start_requests(self):
        for i in range(START, STOP, STEP):
            url = "https://www.zaubacorp.com/company-list/p-{}-company.html".format(i)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        if response.status == 404:
            yield scrapy.Request(response.url, self.parse)
        for sel in response.xpath("//a/@href[contains(., '/company/')]").extract():
            split_ele = sel.split('/')
            if len(split_ele) == 6:
                loader = ItemLoader(item=CompanyItem())
                loader.add_value("cin", [str(split_ele[-1]).strip()])
                loader.add_value("url", [str(sel).strip()])
                loader.add_value("updated", ["today"])
                url = str(sel).strip()
                if url:
                    request = scrapy.Request(url, callback=self.company_parse)
                    request.meta['company'] = loader
                yield request

    def company_parse(self, response):
        if response.status == 404:
            yield scrapy.Request(response.url, self.parse)
        loader = response.meta['company']
        info_list = response.xpath("//div[contains(@class, 'hidden-xs')]").extract()
        info_list += response.xpath("//div[contains(@class, 'col-lg-12')]").extract()
        info_list += response.xpath("//div[contains(@class, 'col-12')]").extract()
        info_dict = {}
        for info in info_list:
            soup = bs4.BeautifulSoup(get_string(info), "lxml")
            if soup.div.b and str(soup.div.b.text).startswith("As on:"):
                info_dict.update({"last_updated": str(soup.div.b.text).split(":")[1].strip()})
            elif soup.h4 and soup.h4.text == "Company Details":
                info_dict.update(self.company_details_parse(soup.findAll("p")))
            elif soup.h4 and soup.h4.text == "Contact Details":
                info_dict.update(self.contact_details_parse(soup.findAll("p")))
        # Rename keys as per needed in Company Item
        for key in info_dict.iterkeys():
            if key in company_keys:  # .has_key(key):
                info_dict[company_keys[key]] = info_dict.pop(key)
        # Get incorporation date if not present
        if "incorporation_date" in info_dict and str(info_dict["incorporation_date"]).strip().startswith("n/a"):
            if info_dict["age_of_company"] and len(info_dict["age_of_company"]) > 1:
                info_dict["incorporation_date"] = derive_date_from_age(info_dict["age_of_company"],
                                                                       info_dict["last_updated"])
            else:
                info_dict["incorporation_date"] = derive_date_from_cin(info_dict["cin"])
        # Mark other fields of Company Item to be empty if not present in dictionary
        for attrib in loader.item.fields.keys():
            if attrib not in info_dict.keys() and attrib not in ["last_updated", "updated"]:
                info_dict[attrib] = ''
        # Remove unnecessary keys
        for key in list(set(info_dict.keys()).difference(loader.item.fields.keys())):
            info_dict.pop(key)
        # Add to loader
        for key, value in info_dict.iteritems():
            loader.add_value(key, value)

        yield loader.load_item()

    def company_details_parse(self, ptag):
        info_dict = dict(map(None, *[iter([str(get_string(p.text)).lower().strip().replace(' ', '_')
                                           for p in ptag if
                                           not str(get_string(p.text)).startswith("Click here")])] * 2))

        return info_dict

    def contact_details_parse(self, ptag):
        info_dict = {}
        for lst in [str(get_string(p.text)).lower().strip().split(':') for p in ptag]:
            if len(lst) > 2:
                # Its a website
                info_dict[str(lst[0]).strip().replace(' ', '_')] = "{0}:{1}".format(str(lst[1]).strip(),
                                                                                  str(lst[2]).strip())
            elif len(lst) > 1:
                info_dict[str(lst[0]).strip().replace(' ', '_')] = str(lst[1]).strip() \
                    if not str(lst[1]).strip().startswith('click here') else ''
            else:
                # Its an address's last part
                info_dict['tmp'] = lst[0]
        if 'tmp' in info_dict and 'address' in info_dict:
            info_dict['address'] = info_dict.pop('tmp') if not info_dict['address'] \
                else " ".join([info_dict.pop('address'), info_dict.pop('tmp')])

        return info_dict
