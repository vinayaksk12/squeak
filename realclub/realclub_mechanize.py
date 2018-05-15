
import re
from utils import get_auth_webpage, EMAIL_REGEX, URL_REGEX

import mechanize
import cookielib

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# The site we will navigate into, handling it's session
br.add_password('http://www.therealclub.com', 'abhishekbarari', 'Jairam121!')
br.open('http://www.therealclub.com')

# View available forms
for form in br.forms():
    form.find_control(id="Email_post").__setattr__("value", "abhishekbarari")
    form.find_control(id="Password_post").__setattr__("value", "Jairam121!")
    br.select_form(nr = 0)
    res = br.submit(name='consubmit')

soup = get_auth_webpage(url="http://www.therealclub.com/Members-Directory/", br=br)
elements = soup.findAll("a", attrs={'href': re.compile(r".*\Profile\b.*")})

user_list = []
for element in elements:
    last_ele = str(element["href"]).split("/")[-1]
    if last_ele not in user_list:
        user_list.append(last_ele)

print(user_list)

elements = soup.findAll("td", attrs={"class": "dxpButton_Office2003Olive"})
for element in elements:
    print(element)