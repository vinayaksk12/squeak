import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Regex for verifying strings for email and url
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
URL_REGEX = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def __if_number_get_string(number):
    converted_str = number
    if isinstance(number, int) or \
            isinstance(number, float):
        converted_str = str(number)
    return converted_str


def get_unicode(strOrUnicode, encoding="utf-8"):
    strOrUnicode = __if_number_get_string(strOrUnicode)
    if isinstance(strOrUnicode, unicode):
        return strOrUnicode
    return unicode(strOrUnicode, encoding, errors="replace")


def get_string(strOrUnicode, encoding="utf-8"):
    strOrUnicode = __if_number_get_string(strOrUnicode)
    if isinstance(strOrUnicode, unicode):
        return strOrUnicode.encode(encoding)
    return strOrUnicode


def derive_date_from_age(age, updated_date):
    age_list = str(age).replace('_', ' ').split(',')
    years = months = days = 0
    for item in age_list:
        if item.endswith("years"):
            years = int(filter(str.isdigit, item))
        elif item.endswith("month"):
            months = int(filter(str.isdigit, item))
        else:
            days = int(filter(str.isdigit, item))
    updated = datetime.strptime(updated_date, "%B %d, %Y")
    # return (updated.replace(year=updated.year - years).replace(month=updated.month - months) -
    #         timedelta(days=days)).strftime("%d_%B_%Y")
    return (updated - relativedelta(years=years, months=months, days=days)).strftime("%d_%B_%Y")


def derive_date_from_cin(cin):
    if len(cin) < 21:
        return 0
    year = re.sub("[a-zA-Z]+", " ", cin).strip().split(" ")[1]
    return datetime(year=int(year), month=01, day=01).strftime("%d_%B_%Y")
