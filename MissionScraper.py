

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
page_filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\theHunter - Missions.htm"
url = "https://www.thehunter.com"
output_filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\missions.txt"
config_filename = r"E:\Dropbox\_PROJECTS\Python\scraping1\config.txt"

mission_list = []
block_list = []
# This are the species listed in the wiki. It doesn't attempt to handle plurals etc. but that hasn't been necessary so far.
region_list = [
    ['Whitehart Island', 'Roosevelt Elk', 'Whitetail Deer', 'Blacktail Deer', 'Coyote', 'Bobcat', 'Turkey'],
    ["Logger's Point" , 'Feral Hog', 'Mule Deer', 'Whitetail Deer', 'Coyote', 'Bobcat', 'Pheasant', 'Cottontail Rabbit'],
    ['Settler Creeks', 'Roosevelt Elk', 'Black Bear', 'Feral Hog', 'Whitetail Deer', 'Bobcat', 'Turkey', 'Cottontail Rabbit'],
    ['Redfeather Falls', 'Moose', 'Roosevelt Elk', 'Black Bear', 'Whitetail Deer', 'Blacktail Deer'],
    ['Hirschfelden', 'Red Deer', 'Wild Boar', 'Roe Deer', 'Red Fox', 'Canada Goose','Pheasant'],
    ['Hemmeldal', 'Moose','Brown Bear','Reindeer', 'Roe Deer', 'Red Fox', 'Eurasian Lynx', 'Willow Ptarmigan'],
    ['Rougarou Bayou', 'Black Bear', 'Feral Hog', 'Whitetail Deer', 'Bobcat', 'Mallard', 'American Black Duck', 'Northern Pintail', 'Gadwall'],
    ['Val des Bois', 'Brown Bear', 'Red Deer', 'Alpine Ibex', 'Roe Deer', 'Red Fox', 'European Rabbit', 'Rock Ptarmigan'],
    ["Bushranger's Run",'Feral Hog','Red Kangaroo','Feral Goat','Red Fox', 'European Rabbit'],
    ['Whiterime Ridge', 'Bison', 'Moose', 'Polar Bear', 'Sitka Deer', 'Dall Sheep', 'Arctic Fox', 'Snowshoe Hare', 'Snow Goose'],
    ['Timbergold Trails', 'Rocky Mountain Elk', 'Grizzly Bear', 'Mule Deer', 'Grey Wolf', 'Puma', 'Bighorn Sheep', 'White-tailed Ptarmigan'],
    ['Piccabeen Bay', 'Water Buffalo', 'Banteng', 'Sambar Deer', 'Rusa Deer', 'Feral Hog', 'Magpie Goose']
    ]


class Mission():
    def __init__(self, m):
        self.active = False
        self.ignore = False
        self.species = []
        self.weapons = []
        self.location = []
        self.scrape(m)
        self.format()
        self.locate()
        self.text = self.text + 'Location: ' + str(self.location) + '\n\n'

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
        self.text = s

    def locate(self):
        # This does not handle some special cases.
        # Like when a region is mentioned by name, but not all of the mission needs to be done there
        # but I am OK with that mission being classified as that region
        # It also does not handle the case where multiple objectives have to be done in the same hunt, thus the mission must be
        # done in the location that has all the species mentioned
        # Or cases where the required location is specified in a way other than by name or by species
        # for the moment, I'm willing to hard code a few of these
        if self.name == "Places To Remember":
            self.location = ['Rougarou Bayou']
            return

        self.location = []
        for region in region_list:  #check region names first, that overrides other keywords
            if (region[0] in self.text):
                self.location.append(region[0])
            if ' ' in region[0]:
                keyword = region[0].replace(' ', '-')   # some mission descriptions say Val des Bois, some say Val-des-Bois
                if (keyword in self.text):
                    self.location.append(region[0])
        if len(self.location) > 0:
            return

        for region in region_list:
            for keyword in region:  # doesn't matter if we check region[0] again
                if (keyword in self.text) and (not region[0] in self.location):
                        self.location.append(region[0])


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

    buffer = "\n\nAVALIABLE (NOT ACTIVATED) MISSIONS\n\n"
    for m in mission_list:
        if m.active == False:
            if not is_blocked(m):
                buffer += m.text
                buffer += "\n\n"

    buffer  += "ACTIVE MISSIONS\n\n"
    for r in region_list:
       buffer  += "=====" + r[0] + "=====\n\n"
       for m in mission_list:
          if r[0] in m.location:
              if m.active == True:
                  if not is_blocked(m):
                      buffer += m.text
                      buffer += "\n\n"

    outputFile = open(output_filename, 'wb')
    outputFile.write(buffer.encode())
    outputFile.close()

if __name__ == '__main__':
    main()


