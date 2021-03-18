#################################
##### Name:
##### Uniqname:
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


class NationalSite:

    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name, address, zipcode, phone, category=None):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
        self.category = category

    def info(self):
        # print format of National Sites and attributes
        return self.name + " (" + self.category + "): " + self.address +\
            " " + self.zipcode


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    dict = {}

    # get all text from nps.gov website
    html = requests.get('https://www.nps.gov').text

    # use Beautiful soup to read in and parse text
    soup = BeautifulSoup(html, 'html.parser')

    ### Created a test file to double check the html import/parsing ###
    # fileTest = open("testFile.txt", "w")
    # fileTest.write(soup.prettify())
    # fileTest.close()

    # narrowed down search to list of states and urls
    search_div = soup.find(role='menu')
    #print(search_div.prettify())

    # looping through search_div to build dictionary
    for state in search_div.find_all('a', href=True):
        #print(state.text)
        #print('https://www.nps.gov' + state['href'])
        if state.text:
            dict[state.text.lower()] = 'https://www.nps.gov' + state['href']

    print(dict)
    #return dict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''
    # get all text from park site passed into function
    parkURL = requests.get(site_url).text

    # use BeautifulSoup to read in and parse text
    soup = BeautifulSoup(parkURL, 'html.parser')

    ### Created a test file to double check the html import/parsing ###
    # fileTest2 = open("testFilePark.txt", "w")
    # fileTest2.write(soup.prettify())
    # fileTest2.close()

    # parkName = soup.find(class_="Hero-title")
    # print(parkName.prettify())

    ### Searching through header to find name/category ###
    parkHeader = soup.find(id='HeroBanner')
    #print(parkHeader.prettify())
    name = parkHeader.find(class_="Hero-title")
    category = parkHeader.find(class_="Hero-designation")


    ### Searching through footer to find location information ###
    search_footer = soup.find(class_='ParkFooter')
    city = search_footer.find(itemprop='addressLocality')
    state = search_footer.find(itemprop='addressRegion')
    zipcode = search_footer.find(itemprop='postalCode')
    phone = search_footer.find(itemprop='telephone')

    # Reassigning names for more clear Return
    name = name.text
    category = category.text
    address = city.text + ", " + state.text
    zipcode = zipcode.text
    phone = phone.text.strip("\n")

    # print(f"Name: {name}")
    # print(f"Category: {category}")
    # print(f"Address: {address}")
    # print(f"Postal Code: {zipcode}")
    # print(f"Telephone: {phone}")

    return NationalSite(name, address, zipcode, phone, category)

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    pass


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    pass
    

if __name__ == "__main__":
    #build_state_url_dict()
    testPart2 = get_site_instance('https://www.nps.gov/isro/index.htm')
    #testPart2 = get_site_instance('https://www.nps.gov/yell/index.htm')
    print(testPart2.info())
