

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
output_filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\missions.txt"
newFile = None

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
    pageFile = open('page.html', 'wb')
    pageFile.write(page_bytes)
    pageFile.close()


def parse_page():
    global newFile

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

    newFile.write(b'ACTIVE MISSIONS\n\n')

    mission_containers = stuff[0].select('div[class = "mission-container"]')
    for mission in mission_containers:
        handle_mission(mission)

    newFile.write(b'\n\nAVAILABLE MISSIONS\n\n')
    stuff = soup.select('div[id = "#available-missions-container"]')
    mission_containers = stuff[0].select('div[class = "mission-container"]')
    for mission in mission_containers:
        handle_mission(mission)



def handle_mission(mission):
    global newFile

    mission_row = mission.select('div[class = "mission-row"]')
    name_text = 'MISSION: ' + mission_row[0].getText().strip() + '\n\n'
    newFile.write(name_text.encode())

    mission_details = mission.select('div[class = "mission-details"]')

    mission_description = mission_details[0].select('div[class = "description"]')
    description_text = mission_description[0].get_text()
    description_text = " ".join(description_text.split()) + '\n'
    newFile.write(description_text.encode())

    mission_objectives = mission_details[0].select('div[class = "objectives"]')
    objective_list = mission_objectives[0].find_all('li')
    if len(objective_list) > 1:
        newFile.write(b'\nObjectives:\n')
    else:
        newFile.write(b'\nObjective:\n')

    for objective in objective_list:
       objective_text = objective.get_text()
       objective_text = " ".join(objective_text.split()) + "\n"
       objective_completed = (objective.i['class'] == "icon-check")
       if objective_completed:
           newFile.write(b'[x] ')
       else:
           newFile.write(b'[ ] ')
       newFile.write(objective_text.encode())

    newFile.write(b'\nReward: ')
    mission_rewards = mission_details[0].select('div[class = "rewards"]')
    reward_list = mission_rewards[0].find_all('li')
    # the html is structured as a list of rewards, although I've never seen more than one
    for reward in reward_list:
        reward_text = reward.get_text().strip()
        newFile.write(reward_text.encode())
    newFile.write(b'\n\n\n\n')


def main():
   global newFile
   # download_page()
   newFile = open(output_filename, 'wb')
   parse_page()
   newFile.close()

if __name__ == '__main__':
    main()


