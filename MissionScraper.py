

"""
MissionScraper.py
For scraping mission data from the website for theHunter Classic

This just automantes what many players do manually on the website: open each
mission and copy & paste the descriptions into a text editor.

"""
from selenium import webdriver
import selenium.common.exceptions
import bs4

# r for raw means we don't have to escape the backslashes
filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\page.html"
url = "https://www.thehunter.com"



def download_page():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10) # seconds
    driver.get(url)
    logged_in = False
    while not logged_in:
        try:
            object_that_appears_after_login = driver.find_element_by_class_name('user-name')
            logged_in = True
        except selenium.common.exceptions.NoSuchElementException:
            pass

    missions_link = driver.find_element_by_link_text('MISSIONS')
    missions_link.click()
    regular_missions_link = driver.find_element_by_link_text('Regular Missions')
    regular_missions_link.click()
    page = driver.page_source  # returns a string
    # open the file in write binary mode ('wb'), and write bytes to it
    # otherwise we may get a UnicodeEncodeError
    page_bytes = page.encode('utf-8')
    newFile = open('page.html', 'wb')
    newFile.write(page_bytes)
    newFile.close()


def parse_page():
    pageFile = open(filename, 'rb')
    page = pageFile.read()
    pageFile.close()

    # html.parser is the default parser, but if you don't specify it you get a warning
    soup = bs4.BeautifulSoup(page, 'html.parser')
    # the id we're looking for starts with a # sign, so we can't use the shorter syntax
    # stuff = soup.select("##active-missions-container")   # select by id doesn't work for this one
    stuff = soup.select('div[id = "#active-missions-container"]')
    # note that this returns a 'bs4.element.ResultSet even if there's only 1 tag in it
    # the Tag we're looking for is stuff[0]

    # text_data = stuff[0].get_text()  # a string
    # print(type(text_data))
    # newFile = open('output.txt', 'wb')
    # newFile.write(text_data.encode('utf-8'))
    # newFile.close()
    # sort of works but result has lots of whitespace etc.
    # better to parse it properly

    for child in stuff[0].descendants:
        if type(child) == bs4.element.Tag: #  ignore whitespace, comments etc.
            print(child.attrs)
            if 'class' in child.attrs:
                if "mission-container" in child['class']:
                    handle_mission(child)


def handle_mission(mission):
    print('FOUND A MISSION')
    print(type(mission))
    print(mission.attrs)
    # print(mission.get_text())
    # mission_row is a ResultSet object
    mission_row = mission.select('div[class = "mission-row"]')
    mission_name = mission_row[0].getText()
    mission_name = mission_name.strip()
    mission_details = mission.select('div[class = "mission-details"]')

    mission_description = mission_details[0].select('div[class = "description"]')
    mission_description = mission_description.strip()

    mission_objectives = mission_details[0].select('div[class = "objectives"]')
    mission_rewards = mission_details[0].select('div[class = "rewards"]')


def main():
   # download_page()
   parse_page()


if __name__ == '__main__':
    main()


