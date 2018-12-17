# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from datetime import datetime, date
import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags


def convert_to_format(value):
    if len(value) < 2:
        value = "01_January_1970"
    try:
        return datetime.strptime(value, "%d_%B_%Y").isoformat().strip().split("T")[0]
    except ValueError as e:
        return datetime.strptime(value, "%B %d, %Y").isoformat().strip().split("T")[0]


def get_days_timestamp(value):
    if value == "today":
        return date.today().strftime("%s")
    elif value == "tomorrow":
        return (date.today() + datetime.timedelta(days=1)).strftime("%s")
    elif value == "yesterday":
        return (date.today() - datetime.timedelta(days=1)).strftime("%s")
    else:
        return datetime.now().strftime("%s")


def get_default(value):
    return value if value else 0


class CompanyItem(scrapy.Item):
    cin = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst(),
    )
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    roc = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    category = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    sub_category = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    registration_number = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    company_class = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    incorporation_date = scrapy.Field(
        input_processor=MapCompose(remove_tags, convert_to_format),
        output_processor=Join(),
    )
    email = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    website = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    address = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    member_count = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    activity = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    status = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    url = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst(),
    )
    last_updated = scrapy.Field(
        input_processor=MapCompose(remove_tags, convert_to_format),
        output_processor=Join(),
    )
    updated = scrapy.Field(
        input_processor=MapCompose(remove_tags, get_days_timestamp),
        output_processor=Join(),
    )
