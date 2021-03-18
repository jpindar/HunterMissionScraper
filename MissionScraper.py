

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
page_filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\page.html"
url = "https://www.thehunter.com"
output_filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\missions.txt"
config_filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\config.txt"

mission_list = []
block_list = []

class Mission():
    def __init__(self, m):
        self.active = False
        self.ignore = False
        self.species = []
        self.weapons = []
        self.scrape(m)
        self.format()

    def format(self):
        s = 'MISSION: ' + self.name + '\n'
        s += self.description + '\n'
        if len(self.objectives) > 1:
            s += 'Objectives:\n'
        else:
            s += 'Objective:\n'
        for objective in self.objectives:
            if objective[0]:
                s += '[x] '
            else:
                s += '[ ] '
            s += objective[1] + '\n'
        if len(self.rewards) > 1:
            s += 'Rewards:\n '
        else:
            s += 'Reward:\n '
        for reward in self.rewards:
           s += "    " +  reward + '\n'
        s += '\n\n'
        self.text = s

    def scrape(self, m):
        mission_row = m.select('div[class = "mission-row"]')
        self.name = mission_row[0].getText().strip()
        mission_details = m.select('div[class = "mission-details"]')

        mission_description = mission_details[0].select('div[class = "description"]')
        description_text = mission_description[0].get_text()
        self.description = " ".join(description_text.split()) # remove excess whitespace

        mission_objectives = mission_details[0].select('div[class = "objectives"]')
        objective_list = mission_objectives[0].find_all('li')

        objectives = []
        for objective in objective_list:
            objective_completed = (objective.i['class'] == ["icon-check"])
            objective_text = objective.get_text()
            objective_text = " ".join(objective_text.split())
            objectives.append([objective_completed, objective_text])

        self.objectives = objectives

        mission_rewards = mission_details[0].select('div[class = "rewards"]')
        reward_list = mission_rewards[0].find_all('li')
        # the html is structured as a list of rewards, although there is rarely more than 1
        self.rewards = []
        for reward in reward_list:
            reward_text = reward.get_text().strip()
            self.rewards.append(reward_text)



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
    pageFile = open(page_filename, 'wb')
    pageFile.write(page_bytes)
    pageFile.close()


def parse_page():
    pageFile = open(page_filename, 'rb')
    page = pageFile.read()
    pageFile.close()
    # html.parser is the default parser, but if you don't specify it you get a warning
    soup = bs4.BeautifulSoup(page, 'html.parser')

    # the ids we're looking for starts with a # sign, so we can't use the shorter syntax
    # stuff = soup.select("##active-missions-container")   # select by id doesn't work for this one

    # note that select() returns a 'bs4.element.ResultSet even if there's only 1 tag in it
    # the Tag we're looking for is stuff[0]

    stuff = soup.select('div[id = "#active-missions-container"]')
    mission_containers = stuff[0].select('div[class = "mission-container"]')
    for m in mission_containers:
        this_mission = Mission(m)
        this_mission.active = True
        mission_list.append(this_mission)

    stuff = soup.select('div[id = "#available-missions-container"]')
    mission_containers = stuff[0].select('div[class = "mission-container"]')
    for m in mission_containers:
        this_mission = Mission(m)
        this_mission.active = False
        mission_list.append(this_mission)


def is_blocked(mission):
    m = mission.text.lower()
    for b in block_list:
       if b in m:
           return True
    return False


def main():
    download_page()
    parse_page()

    configFile = open(config_filename, 'rb')
    with configFile as f:
        for x in f:
            y = x.decode()
            y = y.lower().strip("\r\n\'\"")
            block_list.append(y)

    active_missions = True
    buffer  = "ACTIVE MISSIONS\n\n"
    for m in mission_list:
        if active_missions and m.active == False:
            buffer += "\n\nAVALIABLE MISSIONS\n\n"
            active_missions = False
        if not is_blocked(m):
            buffer += m.text
            buffer += "\n\n"

    outputFile = open(output_filename, 'wb')
    outputFile.write(buffer.encode())
    outputFile.close()

if __name__ == '__main__':
    main()


