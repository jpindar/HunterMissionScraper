

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
mission_list = []


class Mission():
    def __init__(self, m):
        #self.name = b""
        #self.description = b""
        #self.objectives = b""
        #self.reward = b""
        self.active = False
        self.ignore = False
        self.species = []
        self.weapons = []
        self.scrape(m)


    def get_text(self):
        s = self.name
        s += self.description
        s += self.objectives
        s += self.reward
        s += b"\n\n"
        return s

    def scrape(self, m):
        mission_row = m.select('div[class = "mission-row"]')
        name_text = 'MISSION: ' + mission_row[0].getText().strip() + '\n'
        self.name = name_text.encode()

        mission_details = m.select('div[class = "mission-details"]')

        mission_description = mission_details[0].select('div[class = "description"]')
        description_text = mission_description[0].get_text()
        description_text = " ".join(description_text.split()) + '\n' # remove excess whitespace
        self.description = description_text.encode()

        mission_objectives = mission_details[0].select('div[class = "objectives"]')
        objective_list = mission_objectives[0].find_all('li')
        if len(objective_list) > 1:
            buffer = b'Objectives:\n'
        else:
            buffer = b'Objective:\n'

        for objective in objective_list:
            objective_text = objective.get_text()
            objective_text = " ".join(objective_text.split()) + "\n"
            objective_completed = (objective.i['class'] == ["icon-check"])
            if objective_completed:
                buffer += b'[x] '
            else:
                buffer += b'[ ] '
            buffer += objective_text.encode()

        self.objectives = buffer

        buffer = b'Reward: '
        mission_rewards = mission_details[0].select('div[class = "rewards"]')
        reward_list = mission_rewards[0].find_all('li')
        # the html is structured as a list of rewards, although I've never seen more than one
        for reward in reward_list:
            reward_text = reward.get_text().strip()
            buffer += reward_text.encode()
        buffer += b'\n\n'
        self.reward = buffer

    """
    def classify(self):
         # the space after 'dall' is needed because one of the other missions used the word 'dally'
         # TODO: handle this properly
        whiterime_keywords = [b'Whiterime', b'polar',b'arctic',b'sitka', 'snowshoe', b'dall ']
        timbergold_keywords = [b'rocky',b'wolf',b'wolves',b'puma',b'puma',b'bighorn',b'grizzly']
        whiterime_missions = []
        timbergold_missions = []

        mission_data_lowercase = mission_data.lower()
        for keyword in whiterime_keywords:
            if keyword in mission_data_lowercase:
               whiterime_missions.append(mission_data)
               break

        for keyword in timbergold_keywords:
            if keyword in mission_data_lowercase:
               timbergold_missions.append(mission_data)
               break
    """




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
    pageFile = open(filename, 'rb')
    page = pageFile.read()
    pageFile.close()

    # html.parser is the default parser, but if you don't specify it you get a warning
    soup = bs4.BeautifulSoup(page, 'html.parser')

    # the ids we're looking for starts with a # sign, so we can't use the shorter syntax
    # stuff = soup.select("##active-missions-container")   # select by id doesn't work for this one

    # note that select() returns a 'bs4.element.ResultSet even if there's only 1 tag in it
    # the Tag we're looking for is stuff[0]

    output_buffer = b'ACTIVE MISSIONS\n\n'
    stuff = soup.select('div[id = "#active-missions-container"]')
    mission_containers = stuff[0].select('div[class = "mission-container"]')
    for m in mission_containers:
        this_mission = Mission(m)
        this_mission.active = True
        mission_list.append(this_mission)

    output_buffer += b'\n\nAVAILABLE MISSIONS\n\n'
    stuff = soup.select('div[id = "#available-missions-container"]')
    mission_containers = stuff[0].select('div[class = "mission-container"]')
    for m in mission_containers:
        this_mission = Mission(m)
        this_mission.active = False
        mission_list.append(this_mission)




def main():
    # download_page()
    parse_page()

    active_missions = True
    buffer  = b"ACTIVE MISSIONS\n\n"
    for m in mission_list:
        if active_missions and m.active == False:
            buffer += b"\n\nAVALIABLE MISSIONS\n\n"
            active_missions = False
        buffer += m.get_text()
        buffer += b"\n\n"

    outputFile = open(output_filename, 'wb')
    outputFile.write(buffer)
    outputFile.close()

if __name__ == '__main__':
    main()


