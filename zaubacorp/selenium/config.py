# Configuration file for scraping
START = 1 # 1301
STOP = 2  # 1501 # 54374
STEP = 1

# Which source to use, either URL or FILE.
# NOTE: FILE is assumed to be an excel sheet in csv or xlsx format
SOURCE = "file"
SOURCE_URL = "https://www.zaubacorp.com/company-list/p-{}-company.html"
SOURCE_PATH = "2016_Jan_March.xlsx"
