import csv
import time

import bs4
import os
import re
import openpyxl
from loggerd import logger
from utils import get_string


header = ["cin", "company_name", "roc", "company_category", "company_sub_category", "registration_number",
          "class_of_company", "date_of_incorporation", "email_id", "website", "address", "number_of_members",
          "activity", "company_status", "url"]


class Company(object):

    def __init__(self, **kwargs):
        pass


def get_company_list(page=None, user_list=[]):
    if page is not None:
        soup = bs4.BeautifulSoup(page, "lxml")
        elements = soup.findAll("a", attrs={'href': re.compile(r".*\company\b.*")})
        for element in elements:
            split_ele = str(element["href"]).split("/")
            if len(split_ele) == 6 and split_ele[-1] not in user_list:
                user_list.append(split_ele[-1])
    return user_list


def get_companies_from_url(source_location, driver, start, stop):
    driver.get(str(source_location).format(start))

    # Collect company list
    continue_scraping = True
    company_list = []
    counter = 1
    while continue_scraping:
        company_list = get_company_list(driver.page_source, company_list)
        if counter * 30 != len(company_list):
            logger.warning("Company: {idx} => {length}".format(idx=counter, length=len(company_list)))
            time.sleep(1)
            continue
        logger.info("Company: {idx} => {length}".format(idx=counter, length=len(company_list)))
        try:
            next_button = driver.find_element_by_link_text("{:,d}".format(start + counter))
            next_button.click()
            time.sleep(2)
        except Exception as ae:
            logger.exception(msg=ae.message, exc_info=True)
            continue_scraping = False
            continue
        # increment counter to stop at specified stop point
        counter += 1
        if counter + start > stop:
            logger.info(msg="Finished {0} - {1}".format(start, stop - 1))
            continue_scraping = False
            continue
    return company_list


def get_companies_from_file(source_location):
    company_list = []
    path = os.getcwd() + os.sep + "zaubacorp" + os.sep + "read_from" + os.sep + source_location
    if not os.path.exists(path):
        exit(1)
    wb = openpyxl.load_workbook(path)
    sheet = wb.active
    row = column = 1
    while True:
        company = sheet.cell(row=row, column=column)
        if not company.value:
            break
        company_list.append(company.value) if company.value != "CIN" else None
        row += 1

    return company_list


def init_extraction(page=None):
    if page is None:
        exit(1)
    company = Company()
    soup = bs4.BeautifulSoup(page, "lxml")

    info_list = soup.findAll("div", attrs={"class": "col-lg-12"})
    info_list += soup.findAll("div", attrs={"class": "col-12"})
    info_dict = {}
    for info in info_list:
        if info.h4 and info.h4.text == "Company Details":
            soup1 = bs4.BeautifulSoup(str(info.table), "lxml")
            ptag = soup1.findAll("p")
            info_dict = dict(map(None, *[iter([str(get_string(p.text)).lower().strip().replace(' ', '_')
                                               for p in ptag if not str(get_string(p.text)).startswith("Click here")])] * 2))
            if "llp_identification_number" in info_dict:
                info_dict["cin"] = info_dict.pop("llp_identification_number")
            elif "foreign_company_registration_number" in info_dict:
                info_dict["cin"] = info_dict.pop("foreign_company_registration_number")
            else:
                pass
            if "main_division_of_business_activity_to_be_carried_out_in_india" in info_dict:
                info_dict["company_category"] = info_dict.pop("main_division_of_business_activity_to_be_carried_out_in_india")
            if "type_of_office" in info_dict:
                info_dict["company_category"] = info_dict.pop("type_of_office")
            if "description_of_main_division" in info_dict:
                info_dict["company_sub_category"] = info_dict.pop("description_of_main_division")
            if "country_of_incorporation" in info_dict:
                info_dict["roc"] = info_dict.pop("country_of_incorporation")
            for attrib in header:
                if attrib not in info_dict:
                    info_dict[attrib] = ''
        elif info.h4 and info.h4.text == "Contact Details":
            soup1 = bs4.BeautifulSoup(str(info.div), "lxml")
            ptag = soup1.findAll("p")
            contact = {}
            for lst in [str(get_string(p.text)).lower().strip().split(':') for p in ptag]:
                if len(lst) > 2:
                    # Its a website
                    contact[str(lst[0]).strip().replace(' ', '_')] = "{0}:{1}".format(str(lst[1]).strip(), str(lst[2]).strip())
                elif len(lst) > 1:
                    contact[str(lst[0]).strip().replace(' ', '_')] = str(lst[1]).strip() \
                        if not str(lst[1]).strip().startswith('click here') else ''
                else:
                    # Its an address's last part
                    contact['tmp'] = lst[0]
            if 'tmp' in contact and 'address' in contact:
                contact['address'] = contact['tmp'] if not contact['address'] \
                    else "{0} {1}".format([contact['address'], contact['tmp']])
                del contact['tmp']
            info_dict.update(contact)

    for key, value in info_dict.iteritems():
        setattr(company, key, get_string(value).strip().replace('_', ' ') if value is not None and key != "email_id" else '')
    setattr(company, "email_id", get_string(info_dict['email_id']).strip() if 'email_id' in info_dict else '')
    return company


def init_scraping(source, source_location, driver, start, stop):

    company_list = []
    if source == "url":
        company_list = get_companies_from_url(source_location, driver, start, stop)
    else:
        company_list = get_companies_from_file(source_location)

    path = os.getcwd() + os.sep + "results" + os.sep + "{}.csv".format(str(os.path.basename(__file__)).replace(".py", ''))
    status = False
    if not os.path.exists(path):
        status = True
    else:
        company_csv_file = open(path, "r")
        csv_rd = csv.reader(company_csv_file)
        # if csv already has more than 60000 records, move it to some other name and create new one
        total_rows = sum(1 for row in csv_rd)
        company_csv_file.close()
        if total_rows >= 60000:
            filename = os.path.basename(path).replace(".csv", '')
            index = 0
            while os.path.exists("{filename}_{index}.csv".format(filename=filename, index=index)):
                index += 1
            os.rename("{}.csv".format(filename), "{filename}_{index}.csv".format(filename=filename, index=index))
            # Now allow to create a new file with the name
            status = True

    company_csv_file = open(path, "ab+")
    csv_wr = csv.writer(company_csv_file, quoting=csv.QUOTE_ALL)
    if status:
        csv_wr.writerow(header)
    for company in company_list:
        driver.get("https://www.zaubacorp.com/company/SOME-COMPANY-NAME/{cin}".format(cin=company))
        while True:
            company_obj = init_extraction(driver.page_source)
            if hasattr(company_obj, "cin"):
                break
            time.sleep(1)

        try:
            company_obj.url = "https://www.zaubacorp.com/company/{company}/{cin}".format(
                company=str(getattr(company_obj, "company_name")).upper().replace(' ', '-'),
                cin=str(getattr(company_obj, "cin")).strip().upper())
            content = [get_string(getattr(company_obj, key)) for key in header if key != "cin"]
            content.insert(0, str(getattr(company_obj, "cin")).strip().upper())
            if hasattr(company_obj, "cin"):
                csv_wr.writerow(content)
        except Exception as ae:
            logger.exception(msg=[key for key in dir(company_obj) if not key.startswith('_')])
            logger.exception(msg="Company CIN: {}".format(getattr(company_obj, "cin")), exc_info=True)
            continue
        time.sleep(1)

    company_csv_file.close()
