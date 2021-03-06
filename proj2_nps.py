#################################
##### Name: Jana Muhic
##### Uniqname: jmuhic
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
    ''' Make a dictionary that maps state name to state page
    url from "https://www.nps.gov"

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

        # add state url dictioary to cache for future searches
        add_to_cache('dict', dict)

    return dict  # will return cached dict if found


def get_site_instance(site_url):
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    siteInstance: obj
        a national site instance (obj)
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

        # Reassigning names.text for more understandable Return format
        name = name.text

        # Some parks do not have a category listed; default 'no category'
        if category.text != '':
            category = category.text
        else:
            category = "no category"

        # handling exceptions where address information is missing
        if city != None and state != None:
            address = city.text + ", " + state.text
        else:
            address = ""

        if zipcode != None:
            zipcode = zipcode.text.rstrip()
        else:
            zipcode = ""

        if phone != None:
            phone = phone.text.strip("\n")
        else:
            phone = ""

        # setting site instance (to be returned & cached)
        siteInstance = NationalSite(name, address, zipcode, phone, category)
        # since site instance doesn't already exist, add to cache file
        # toDict converts to format that can be saved to cache
        add_to_cache(site_url, siteInstance.toDict())
    else: # return instance from cache
        siteInstance = NationalSite(siteInstance['name'],\
            siteInstance['address'], siteInstance['zipcode'],\
            siteInstance['phone'], siteInstance['category'])


    return siteInstance  # will return cached instance if found

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    site_inst_list: list of objects
        a list of national site instances
    '''
    # Set list to populate and URLs to build from
    list = []
    site_inst_list = []
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

        add_to_cache(state_url, list)

    # building list of national site instances for state
    # if list in cache, will build from existing list
    for item in list:
        site_inst_list.append(get_site_instance(item))

    return site_inst_list


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    results: dict
        a converted API dict return from MapQuest API
    '''
    results = []
    results = check_cache(site_object.name)

    # will execute API if results not already in cache
    if results is None:
        mapkey = secrets.MAPQUEST_API_KEY
        mapZip = site_object.zipcode
        map_baseurl = 'http://www.mapquestapi.com/search/v2/radius?'

        params = {
            'radius' : '10',
            'key' : mapkey,
            'maxMatches' : '10',
            'origin' : mapZip,
            'ambiguities' : 'ignore',
            'outFormat' : 'json'
        }

        output = requests.get(map_baseurl, params=params)
        results = json.loads(output.text)
        # results added to cache
        add_to_cache(site_object.name, results)

    # executes print_mapquest_result function for display to user
    print_mapquest_results(site_object, results)

    return results  # dict return from mapquest API search

def print_mapquest_results(site_object, results):
    '''
    Takes in the results from nearby places search (Mapquest)
    and converts the results into a formatted print out.

    Parameters:
    -----------
    site_object: object
        NationalSite instance (obj) of selected park
    results: dict
        dict of results from Mapquest API Search

    Returns:
    --------
    None
    '''
    list_loc = {
        'name' : [],
        'category' : [],
        'address' : [],
        'city' : []
    }

    # Not all 'index' sites for parks have a listed address
    if site_object.zipcode == '':
        print('No Address Found.  Please make another selection.\n')
    else: # append values to list_loc dictionary (building dict)
        for location in results['searchResults']:
            list_loc['name'].append(location['name'])
            if location['fields']['address'] == '':
                list_loc['address'].append('no address')
            else:
                list_loc['address'].append(location['fields']['address'])
            if location['fields']['group_sic_code_name_ext'] == '':
                list_loc['category'].append('no category')
            else:
                list_loc['category'].append(location['fields']\
                    ['group_sic_code_name_ext'])
            if location['fields']['city'] == '':
                list_loc['city'].append('no city')
            else:
                list_loc['city'].append(location['fields']['city'])

        # Format for header of mapquest results (nearby results)
        print(40 * '-')
        print(f"Places near", site_object.name.title())
        print(40 * '-')

        # Printing nearby results in proper format
        for i in range(len(list_loc['name'])):
            print("- {0} ({1}): {2}, {3}".format(list_loc['name'][i],\
                list_loc['category'][i], list_loc['address'][i],\
                list_loc['city'][i]))


def print_results(search_term, state_sites):
    '''
    Takes in the search term entered by the user
    Returns a formatted list of the State Parks.

    Parameters:
    -----------
    search_term: string
        State entered by the user

    state_sites: list
        List of NationalSite instances for
        the selected state

    Returns:
    --------
    None
    '''
    count = 0

    results = []
    printed_results = []

    # Assigning index value to each instance returned
    # and adding to a list
    for site in state_sites:
        count += 1
        site.index = count
        results.append([site.index, site.info()])

    print(40 * '-')
    print(f"List of National Sites in", search_term.capitalize())
    print(40 * '-')

    # Formatting values in results list for proper printing
    for i in results:
        printed_results.append(print("[{0}] {1}".format(i[0],i[1])))

    return printed_results


def handle_alpha(search_term, state_sites):
    '''
    Handles a search with an alpha (valid state string value)

    Parameter:
    ----------
    search_term: str
        State entered by the user

    state_sites: list of objects
        List of NationalSite instances for the selected state

    Returns:
    --------
    ret(list): list of parks for selected state
    '''
    ret = print_results(search_term, state_sites)

    return ret


def handle_numeric(search_term, state_sites):
    '''
    Handles a search with a numeric value and returns list
    of nearby places if found

    Parameter:
    ----------
    search_term: string
        user-entered index value for selected park
    state_sites: list of objects
        list of state park objects

    Returns:
    --------
    park_obj: object
        returns NationalSite instance of selected park
    '''
    search_term = int(search_term)

    for park_obj in state_sites:
        if park_obj.index == search_term:
            return(park_obj)


def check_cache(key):
    '''
    Checks the cache to see if the data has already been run
    and stored in cache.  Returns value if found.

    Parameters:
    -----------
    key: string
        key from key,value pair in cache

    Returns:
    --------
    value: string
        content of key in dict, if found
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
    key: string
        key from key,value pair in cache

    value: string
        contents of key

    Returns:
    --------
    None
    '''
    # creating key,value pair for cache file
    json_cache[key] = value

    # writing new key,value pair to cache file
    with open("cache2.json", "w") as cache:
        json.dump(json_cache, cache)

# Initializing setup of cache
json_cache = {}
path = 'cache2.json'

# if the cache file exist, read from that file
if os.path.isfile(path):
    with open('cache2.json') as f:
        json_cache = json.load(f)


if __name__ == "__main__":
    # initializing StateDict for user search in While loop
    stateDict = {}
    stateDict = build_state_url_dict()

    # initializing search variable
    state_search = ""

    while True:
        if state_search == "":  # for initial search
            try:
                state_search = input("\nEnter a state name (e.g. Michigan, michigan) or 'exit': ")
                state_search = state_search.lower()
                if state_search == 'exit':
                    print("\n")
                    exit()
                else:
                    #return list results from search
                    state_searchURL = stateDict[state_search]
                    state_sites = get_sites_for_state(state_searchURL)
                    handle_alpha(state_search, state_sites)
            except KeyError:
                state_search = ""
                print("Oops! That is an invalid entry. Please make a different selection.")
        else:  # run if initial search has already been completed
            try:
                state_search = input("\nChoose the number for detail search or 'exit' or 'back': ")
                if state_search.lower() == 'exit':
                    print("\n")
                    exit()
                elif str.isnumeric(state_search):  # run to find nearby places for park
                    # if numeric search selected is out of range, error
                    if (int(state_search) <= 0)\
                         or (int(state_search) > len(state_sites)):
                        print('Search is out of range.  Please try again.')
                    else:  # return list of results from mapquest, maxMatch = 10
                        site_obj_find = handle_numeric(state_search, state_sites)
                        nearby_results = get_nearby_places(site_obj_find)
                # if user enters 'back', clear search value to return to Step 1
                elif state_search.lower() == 'back':
                    state_search = ""
                else:
                    print('Oops! That is an invalid entry. Please make a different selection.')
            except KeyError:
                print('Oops! That is an invalid entry. Please make a different selection.')



   ######## COMMENTED OUT BLOCK USED TO TEST ################
    # # Allow user to enter a state (full name) - not case sensitive
    # userState = input("Enter a state name (e.g. Michigan, michigan) or 'exit': ")

    # # Take user's input and produce a list of results
    # userState = userState.lower()  # not case sensitive
    # userStateURL = stateDict[userState]  # grab StateURL from stateDict
    # print_results(userState, userStateURL)  # print results from user's search

    # results = get_nearby_places(NationalSite(name='Isle Royale', address='Houghton, MI', zipcode='49931', phone='', category='National Park'))
    # print_mapquest_results(results)

    # state_search_list = []
    # search_term = ""
    ############################################################