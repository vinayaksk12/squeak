from selenium import webdriver
import bs4
import re
import csv
import time
from utils import EMAIL_REGEX, URL_REGEX


class User(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "")
        self.username = kwargs.get("username", "")
        self.name = kwargs.get("name", "")
        self.company = kwargs.get("company", "")
        self.designation = kwargs.get("designation", "")
        self.email = kwargs.get("email", "")
        self.website = kwargs.get("website", "")
        self.birthdate = kwargs.get("birhdate", "")
        self.link = kwargs.get("link", "")
        self.experties = kwargs.get("experties", "")
        self.aooperations = kwargs.get("aooperations", "")
        self.noemployee = kwargs.get("noemployee", "")
        self.company_profile = kwargs.get("company_profile", "")
        self.mobile = kwargs.get("mobile", "")
        self.landline = kwargs.get("landline", "")
        self.fax = kwargs.get("fax", "")
        self.address = kwargs.get("address", "")
        self.twitter = kwargs.get("twitter", "")
        self.facebook = kwargs.get("facebook", "")
        self.linkedin = kwargs.get("linkedin", "")
        self.bbn = kwargs.get("bbn", "")
        self.skype = kwargs.get("skype", "")
        self.msn = kwargs.get("msn", "")
        self.yahoo = kwargs.get("yahoo", "")


def get_username(page=None, user_list=[]):
    if page is not None:
        soup = bs4.BeautifulSoup(page, "lxml")
        elements = soup.findAll("a", attrs={'href': re.compile(r".*\Profile\b.*")})
        for element in elements:
            split_ele = str(element["href"]).split("/")
            if split_ele[0] == "Profile" and split_ele[-1] not in user_list:
                user_list.append(split_ele[-1])
    return user_list


def init_extraction(page=None):
    if page is None:
        exit(1)
    user = User()
    soup = bs4.BeautifulSoup(page, "lxml")

    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblUserName"})
    user.username = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblName"})
    user.name = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblCompany"})
    user.company = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblDesignation"})
    user.designation = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblEmail"})
    text = val.text.encode('utf-8').strip() if val is not None else ""
    user.email = text if text and EMAIL_REGEX.match(text) else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblWebsite"})
    user.website = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_Birthday"})
    user.birthdate = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_Expertise1"})
    user.experties = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_AreasofOperation1"})
    user.aooperations = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_Employees1"})
    user.noemployee = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_Company_Profile1"})
    user.company_profile = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblMobile"})
    user.mobile = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblLandline"})
    user.landline = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblFax"})
    user.fax = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblAddress"})
    user.address = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lbltwitter"})
    user.twitter = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblfacebook"})
    user.facebook = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("span", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_lblICQ"})
    user.bbn = val.text.encode('utf-8').strip() if val is not None else ""
    val = soup.find("a", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_Msg_Skype"})
    user.skype = val["href"].encode('utf-8').strip().replace("skype:", "").replace("?", "") if val is not None else ""
    val = soup.find("a", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_MsgMSN"})
    user.msn = val["href"].encode('utf-8').strip().replace("msnim:chat?contact=", "") if val is not None else ""
    val = soup.find("a", attrs={"id": "ctl00_ContentPlaceHolderRight_ASPxPageControl1_MsgYIM"})
    user.yahoo = val["href"].encode('utf-8').strip().replace("http://edit.yahoo.com/config/send_webmesg?.target=", "").replace("&.src=pg", "") if val is not None else ""

    return user


def init_scraping():
    driver = webdriver.Firefox()
    driver.implicitly_wait(7)

    driver.get("http://www.therealclub.com")
    acc_trigger = driver.find_elements_by_class_name("acc-trigger")

    for index, trigger in enumerate(acc_trigger):
        trigger.click()
        if index == 2:
            break

    username = driver.find_element_by_id("Email_post")
    password = driver.find_element_by_id("Password_post")

    username.send_keys("abhishekbarari")
    password.send_keys("Jairam121!")

    driver.find_element_by_id("consubmit").click()

    driver.find_element_by_id("ctl00_menu1_ASPxMenu1_DXI6_T").click()
    driver.find_element_by_id("ctl00_menu1_ASPxMenu1_DXI6i1_T").click()

    continue_scraping = True
    user_list = []
    counter = 0
    while continue_scraping:
        user_list = get_username(driver.page_source, user_list)
        next_button = driver.find_elements_by_class_name("dxpButton_Office2003Olive")
        for button in next_button:
            attrib = button.get_attribute("onclick")
            if attrib is not None and "PBN" in attrib:
                try:
                    button.click()
                    time.sleep(2)
                except Exception as ae:
                    print(ae)
            elif attrib is None and len(user_list) > 5000:
                continue_scraping = False
                break
            else:
                pass
        counter += 1
        print("Users: {idx} => {length}".format(idx=counter, length=len(user_list)))

    user_csv_file = open("therealclub.csv", "wb")
    csv_wr = csv.writer(user_csv_file, quoting=csv.QUOTE_ALL)
    csv_wr.writerow(["username", "name", "company", "designation", "email", "website", "birthdate", "link",
                     "twitter", "facebook", "bbn", "skype", "msn", "yahoo",
                     "experties", "areas of operation", "no of employees", "mobile", "landline", "fax",
                     "address", "company profile"])
    for user in user_list:
        driver.get("http://www.therealclub.com/Members-Directory/Profile/{user}".format(user=user))
        userO = init_extraction(driver.page_source)
        if userO.username:
            userO.link = "http://www.therealclub.com/Members-Directory/Profile/{user}".format(user=user)
            csv_wr.writerow([userO.username, userO.name, userO.company, userO.designation, userO.email, userO.website,
                             userO.birthdate, userO.link, userO.twitter, userO.facebook, userO.bbn,
                             userO.skype, userO.msn, userO.yahoo, userO.experties, userO.aooperations, userO.noemployee,
                             userO.mobile, userO.landline, userO.fax, userO.address, userO.company_profile])

    driver.close()

init_scraping()