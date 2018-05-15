__author__ = 'leena'


import bs4
import requests
import csv

from utils import get_anonym_webpage, EMAIL_REGEX, URL_REGEX


class Space(object):
    def __init__(self,title,no_of_rooms,street,city,state,pincode,phone,fax,email,website,banquet_facility,ownership,managing_director,director,general_manager):
        self.title = title,
        self.no_of_rooms = no_of_rooms,
        self.street = street,
        self.city = city,
        self.state = state,
        self.pincode = pincode,
        self.phone = phone,
        self.fax = fax,
        self.email = email,
        self.website = website,
        self.banquet_facility = banquet_facility,
        self.ownership = ownership,
        self.managing_director = managing_director,
        self.director = director,
        self.general_manager = general_manager

def init_scraping(start, end):
    csv_file = open("fhrai_hotel_list.csv", "wb")
    csv_wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
    csv_wr.writerow(["Title", "No of rooms", "Street", "City", "State", "Pincode", "Phone", "Fax", "Email","Websiite","Banquet Facility" ,"Ownership" ,
                     "Managing Director" , "Director" ,"General Manager" ,"URL"])
    name_list = ["Hotel Name", "Total No of Rooms", "Ownership", "Halls", "Managing Director" ,"Director" ,"General Manager","Address","Contact"]
    space_list = []
    for counter in range(start, end):
      space = {}
      url = "http://www.fhrai.com/dFHrai/hotsearch.asp?hotid={counter}".format(counter=counter)
      soup = get_anonym_webpage(url=url)
      if(soup != None) :
        space['url'] = url if url else ''
        table =  soup.find_all("tr")
        for row in table:
         cells = row.findAll("td")
         for idx, cell in enumerate(cells[1:61]):
             for item in name_list:
                 nameValue = cell.text.strip().find(item)
                 if nameValue == 0:
                     if item == "Hotel Name":
                         name = cells[idx+2].text.strip()
                         space['title'] = name.encode('utf-8').strip() if name else ''
                     if item == "Total No of Rooms":
                         rooms=cells[idx+2].text.strip()
                         space['no_of_rooms'] = rooms.encode('utf-8').strip() if rooms else ''
                     if(item == "Ownership"):
                         owner=cells[idx+1].text.strip()
                         ownership = ([x.strip() for x in owner.split(':')][1])
                         space['ownership'] = ownership.encode('utf-8').strip() if ownership else ''
                     if(item == "Halls"):
                         banquet = cells[idx+1].text.strip()
                         hall_index = (banquet.index("Halls :") + len("Halls :")) if "Halls :" in banquet else -1
                         banquet_facility = banquet[hall_index:len(banquet)].strip() if hall_index > -1 else ''
                         space['banquet_facility'] = banquet_facility.encode('utf-8').strip() if banquet_facility else ''
                     if(item == "Managing Director" or item == "Director" or item == "General Manager"):
                         value = cells[idx+1].text.strip()
                         exact_value = value[len(item):len(value)].strip()
                         space[item] = exact_value.encode('utf-8').strip() if exact_value else ''

                     if(item == "Address"):
                         address=cells[idx+4].text.strip()
                         city_index=address.index("City :")if "City :" in address else -1
                         pincode_index=address.index(" PinCode :")if "PinCode :" in address else -1
                         state_index=address.index("State :")if "State :" in address else -1

                         if(city_index > -1):
                             basicAdd = address[0 : city_index].strip()
                         else :
                             basicAdd = address[0 : state_index].strip()

                         if(city_index > -1 and pincode_index > -1):
                             city = address[city_index + len("City :") : pincode_index].strip()
                         elif(city_index > -1 and pincode_index == -1):
                             city = address[city_index + len("City :") : state_index].strip() if state_index >-1 else ''
                         elif(city_index == -1 and pincode_index > -1):
                             city = ""

                         if(pincode_index > -1 and state_index > -1):
                             pincode = address[pincode_index + len("Pincode :"):state_index].strip()
                         elif(pincode_index > -1 and state_index == -1):
                             pincode = address[pincode_index + len("Pincode :"):len(address) ].strip()
                         elif(pincode_index == -1 and state_index > -1):
                             pincode= ""
                         pincode = pincode.replace(":","").strip()

                         if(state_index > -1) :
                             state = address[state_index + len("State :"):len(address)].strip()
                         else :
                             state = ""

                        # basicAdd = address[0:city_index].strip()
                        #city = address[city_index + len("City :"):pincode_index].strip()
                        # pincode = address[pincode_index + len("PinCode : "):state_index].strip()

                         space['street'] = basicAdd.encode('utf-8').strip() if basicAdd else ''
                         space['city'] = city.encode('utf-8').strip() if city else ''
                         space['state'] = state.encode('utf-8').strip() if state else ''
                         space['pincode']= pincode.encode('utf-8').strip() if pincode else ''

                     if item == "Contact" and not (hasattr(space, 'phone') or hasattr(space, 'fax') or hasattr(space, 'email') or hasattr(space, 'website')):
                         contact = cells[idx+4].text.strip()
                         phone_index = contact.index("Phone :") if "Phone" in contact else -1
                         fax_index = contact.index("Fax :") if "Fax" in contact else -1
                         email_index = contact.index("E-Mail :") if "E-Mail" in contact else -1
                         website_index = contact.index("Website") if "Website" in contact else -1

                         if(phone_index > -1 and fax_index > -1):
                           phone = contact[phone_index + len("Phone :"): fax_index].strip()
                         elif(phone_index > -1 and fax_index == -1):
                           if(email_index != -1):
                            phone = contact[phone_index + len("Phone :") : email_index].strip()
                           else :
                            phone = contact[phone_index + len("Phone :") : website_index].strip()
                         elif(phone_index == -1 and fax_index > -1):
                            phone = ""


                         if(fax_index > -1 and email_index > -1):
                           fax = contact[fax_index + len("Fax :"):email_index].strip()
                         elif(fax_index > -1 and email_index == -1):
                            fax = contact[fax_index + len("Fax :"):website_index ].strip()
                         elif(fax_index == -1 and email_index > -1):
                             fax = ""

                         if(email_index > -1 and website_index > -1):
                           email = contact[email_index + len("Email :"):website_index].strip()
                         elif(email_index > -1 and website_index == -1):
                            email = contact[email_index + len("Email :"):-1 ].strip()
                         elif(email_index == -1 and website_index > -1):
                             email = ""

                         email = email.replace(":","").strip()

                         if(fax_index > -1 and email_index > -1):
                           fax = contact[fax_index + len("Fax :"):email_index].strip()
                         elif(fax_index > -1 and email_index == -1):
                            fax = contact[fax_index + len("Fax :"):website_index ].strip()
                         elif(fax_index == -1 and email_index > -1):
                             fax = ""

                        # phone = contact[phone_index + len("Phone :"):fax_index].strip() if phone_index > -1  else ''
                        # fax = contact[fax_index + len("Fax :"):email_index].strip() if fax_index > -1 else ''
                        # email = contact[email_index + len("E-mail :"):website_index].strip() if email_index > -1 else ''
                         website = contact[website_index + len("Website :"):len(contact)].strip() if website_index > -1 else ''

                         space['phone'] = phone.encode('utf-8').strip() if phone else ''
                         space['fax'] = fax.encode('utf-8').strip() if fax else ''
                         space['email'] = email.encode('utf-8').strip() if email and EMAIL_REGEX.match(email) else ''
                         space['website'] = website.encode('utf-8').strip() if website else ''

                     '''
                     spaceObj = Space(title=name, no_of_rooms= rooms, street=basicAdd,  city=city, state=state,  pincode=pincode,
                             phone=phone, fax=fax, email=email, website=website ,banquet_facility = banquet_facility , ownership= ownership,managing_director=manager_value
                               ,director=director_value,general_manager=general_value)
                     '''
      if space:
        csv_wr.writerow([space.get("title",""), space.get("no_of_rooms",""), space.get("street",""), space.get("city",""), space.get("state",""),
                           space.get("pincode",""), space.get("phone",""), space.get("fax",""), space.get("email",""), space.get("website",""),
                           space.get("banquet_facility",""),space.get("ownership","") , space.get("Managing Director") ,space.get("Director"),
                           space.get("General Manager"), space.get("url")])

              #space_list.append(spaceObj)
    return space_list

print("Start scraping")
#init_scraping(355845,355876)
init_scraping(354000,356550)
print("end")

