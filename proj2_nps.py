#################################
##### Name:
##### Uniqname:
#################################

from bs4 import BeautifulSoup
import requests
import json
import os
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
        self.index = 0

    def info(self):
        # print format of National Sites and attributes
        return self.name + " (" + self.category + "): " + self.address +\
            " " + self.zipcode

    def toDict(self):
        # convert National Site object to dictionary
        jsonDict = {
            'name' : self.name,
            'address' : self.address,
            'zipcode' : self.zipcode,
            'phone' : self.phone,
            'category' : self.category
        }

        return jsonDict

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
    dict = check_cache('dict')

    if dict is None:
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

    add_to_cache('dict', dict)
    return dict  # will return cached dict if found

def get_site_instance_alt(site_url):
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
    # fileTest2 = open("testFilePark_NEW.txt", "w")
    # fileTest2.write(soup.prettify())
    # fileTest2.close()

    # parkName = soup.find(class_="Hero-title")
    # print(parkName.prettify())

    ### Searching through header to find name/category ###
    parkHeader = soup.find(id='HeroBanner')
    #print(parkHeader.prettify())
    name = parkHeader.find(class_="Hero-title -long")
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

    return NationalSite(name, address, zipcode, phone, category)

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
    siteInstance = check_cache(site_url)

    if siteInstance is None:
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
        address = ""
        if city != None and state != None and zipcode != None:
            address = city.text + ", " + state.text
            zipcode = zipcode.text
        else:
            city = ""
            state = ""
            zipcode = ""
        phone = phone.text.strip("\n")

        siteInstance = NationalSite(name, address, zipcode, phone, category)
        # since site instance doesn't already exist, add to cache file
        add_to_cache(site_url, siteInstance.toDict())
    else:
        siteInstance = NationalSite(siteInstance['name'], siteInstance['address'], siteInstance['zipcode'], siteInstance['phone'], siteInstance['category'])

    return siteInstance

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
    # Set list to populate and URLs to build from
    list = []
    list = check_cache(state_url)

    if list is None:
        list = []
        baseURL = 'https://www.nps.gov' # start of URL
        indexURL = 'index.htm'  # end of URL

        # get all text from State site passed into function
        stateParksURL = requests.get(state_url).text

        # use BeautifulSoup to read in and parse text
        soup = BeautifulSoup(stateParksURL, 'html.parser')

        # Search for list of Parks for State
        topList = soup.find(id='parkListResults')
        # URLs all contained in 'h3' headers
        headers = topList.find_all('h3')

        # Loop through headers to pull URL tags for each State park.
        for parks in headers:
            temp = parks.find('a', href=True)
            tempURL = temp['href']
            list.append(baseURL + tempURL + indexURL)

    #print(list)
    add_to_cache(state_url, list)
    return list

    ### Created a test file to double check the html import/parsing ###
    # fileTest3 = open("testFileStateParks.txt", "w")
    # fileTest3.write(soup.prettify())
    # fileTest3.close()


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

def print_results(userState, userStateURL):
    '''
    Takes in the URL for State entered by the user.
    Returns a formatted list of the State Parks.

    Parameters:
    -----------
    userStateURL(URL): URL for user's selected State

    Returns:
    --------
    None
    '''
    count = 0
    listSites = get_sites_for_state(userStateURL)

    results = []
    for site in listSites:
        #formatSiteList.append(get_site_instance(site).info())
        count += 1
        site_inst = get_site_instance(site)
        site_inst.index = count
        results.append([site_inst.index, site_inst])

    print(40 * '-')
    print(f"List of National Sites in ", userState.capitalize())
    print(40 * '-')

    for i in results:
        print("[{0}] {1}".format(i[0],i[1].info()))
    print("\n")


def check_cache(key):
    '''
    Checks the cache to see if the data has already been run
    and stored in cache.  Returns value if found.

    Parameters:
    -----------
    key (string): key from key,value pair in cache

    Returns:
    --------
    value: content of key if found
    '''
    if key in json_cache:
        print('Using cache')
        return json_cache[key]
    else:
        print('Fetching')
        return None


def add_to_cache(key, value):
    '''
    Adds key, value pair to json_cache file

    Parameters:
    -----------
    key (string): key from key,value pair in cache
    value: contents of key

    Returns:
    --------
    None
    '''
    # creating key,value pair for cache file
    json_cache[key] = value

    # writing new key,value pair to cache file
    with open("cache.json", "w") as cache:
        json.dump(json_cache, cache)


if __name__ == "__main__":
    # initializing cache and path
    json_cache = {}
    path = 'cache.json'

    # if the cache file exist, read from that file
    if os.path.isfile(path):
        with open('cache.json') as f:
            json_cache = json.load(f)

    # initializing StateDict for user search in next step
    stateDict = {}
    stateDict = build_state_url_dict()

    # Allow user to enter a state (full name) - not case sensitive
    userState = input("Enter a state name (e.g. Michigan, michigan) or 'exit': ")

    # Take user's input and produce a list of results
    userState = userState.lower()  # not case sensitive
    userStateURL = stateDict[userState]  # grab StateURL from stateDict
    print_results(userState, userStateURL)  # print results from user's search
