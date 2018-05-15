__author__ = 'rahul'

'''
This script scrapes data from http://www.workspot.in/
'''

import bs4
import requests
import csv
import re
from pymongo import MongoClient

from utils import EMAIL_REGEX, URL_REGEX
from utils import get_anonym_webpage

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.workspot


class Space(object):

    def __init__(self,title,person,email,phone,street,locality,website):
        self.title = title,
        self.person = person,
        self.email = email,
        self.phone = phone,
        self.street = street,
        self.locality = locality,
        self.website = website

fieldmap = {"name": "title",
        "contactPerson": "person",
        "email": "email",
        "telephone": "phone",
        "streetAddress": "street",
        "addressLocality": "locality",
        "website": "website",
        "Source" : "source",
        "col-md-8": "col-md-8"
}


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_space(soup=None, attributes={}, tags={}):
    space = {}
    if soup:
        for key, value in attributes.iteritems():
            for item in value:
                element = soup.findAll(tags[item], {key: item})
                space = get_text(item=item, elements=element, space=space, key=key)
    return space


def get_text(item, elements=[], space={}, key="class"):
    for element in elements:
        text = element.find(text=True)
        if text is None:
            continue

        text = text.encode('utf-8').strip()
        if text and len(text) <= 0:
            continue
        elif text and len(text) > 0:
            # check if email id
            if EMAIL_REGEX.match(text):
                item = "email"
            # check if url
            elif URL_REGEX.match(text):
                item = "website"
            elif key == "class" and not hasNumbers(text):
                item = "contactPerson"
            else:
                # Other fields. leave as it is
                if key == "class":
                    continue
            if item == "addressLocality" and fieldmap[item] in space and len(space.get(fieldmap[item], '')) > 0:
                space[fieldmap[item]] += ", " + text
            else:
                space.update({fieldmap[item]: text})
        else:
            if fieldmap[item] in space and len(space.get(fieldmap[item], '')) <= 0:
                space.update({fieldmap[item]: 0})
    return space


def init_scraping(start, end):
    attributes = {
        "itemprop": ["name", "telephone", "streetAddress", "addressLocality"],
        "class": ["col-md-8"]
    }

    tags = {"name": "a",
            "telephone": "span",
            "streetAddress": "span",
            "addressLocality": "span",
            "col-md-8": "div"
    }
    csv_file = open("workspot_space_list.csv", "wb")
    if not csv_file:
        exit(1)
    csv_wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
    csv_wr.writerow(["title", "person", "email", "phone", "street", "locality", "website", "url", "source"])
    space_list = []
    for counter in range(start, end):
        url = "http://www.workspot.in/city/mumbai/chembur-deonar/gnmv-spaces/{counter}".format(counter=counter)
        soup = get_anonym_webpage(url=url)
        space = get_space(soup=soup, attributes=attributes, tags=tags)
        #spaceObj = Space(title=space.get("title", ""), person=space.get("person", ""),email= space.get("email",""),
        #                 phone = space.get("phone" ,""),street= space.get("street","") ,locality= space.get("locality",""),
        #                 website= space.get("website",""))
        #spaceObj.source = "workspot"
        if space and len(space) > 1:
            spaceObj = Space(title=space.get("title", ""), person=space.get("person", ""),email= space.get("email",""),
                             phone = space.get("phone" ,""),street= space.get("street","") ,locality= space.get("locality",""),
                             website= space.get("website",""))
            spaceObj.url = url
            space['url'] = url
            csv_wr.writerow([space.get("title", ""),space.get("person", ""),space.get("email",""),space.get("phone",""),
                             space.get("street",""),space.get("locality",""),space.get("website",""), space.get("url",""),"workspot" ])

            '''csv_wr.writerow([spaceObj.title, spaceObj.person, spaceObj.email, spaceObj.phone, spaceObj.street,
                             spaceObj.locality, spaceObj.website, spaceObj.url, "workspot"])
            '''

            post = db.workspot.insert({"title":space.get("title",""), "person" : space.get("person", ""), "email" : space.get("email",""),
                                          "phone" : space.get("phone","") ,"street" : space.get("street" ,""),"locality" : space.get("locality" ,""),
                                           "website" : space.get("website","") ,"url" : space.get("url","") , "source" : "workspot"})

            space_list.append(spaceObj)

    return space_list


print("Starting scraping")
init_scraping(1,250)
print("Scraping completed")