import requests
import json
import datetime
import pytz
import string
from serpapi import GoogleSearch
import bs4


FREE_GAMES_URL = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=IL&allowCountries=IL'
GAME_URL = 'https://www.epicgames.com/store/en-US/p/'
THURSDAY = 3
WEDNESDAY = 2

class Game:
    def __init__(self, name, image, url='', rating=None, original_price=None, current_price=None, discount_pct=None):
        self._name = name
        self._image = image
        self._url = url
        self._rating = rating
        self._original_price = original_price
        self._current_price = current_price
        self._discount_pct = discount_pct

    def get_name(self):
        return self._name

    def get_image(self):
        return self._image

    def get_url(self):
        return self._url

    def get_rating(self):
        return self._rating

    def get_original_price(self):
        return self._original_price

    def get_current_price(self):
        return self._current_price

    def get_discount_pct(self):
        return self._discount_pct


class GameNotFoundException(Exception):
    def __init__(self, game_name):
        super().__init__('meow! the game "{}" was not found. :('.format(game_name))


def get_game_url(name):
    return GAME_URL + name.lower().replace(' ', '-')

def get_last_new_games_date():
    timezone = pytz.timezone('Asia/Jerusalem')
    date = datetime.datetime.now(timezone)

    if date.weekday() == THURSDAY and date.hour >= 18:
            return date.date()

    else:
        if date.date.weekday() == THURSDAY:
            date -= datetime.timedelta(days=1)

        while date.weekday() != THURSDAY:            
            date -= datetime.timedelta(days=1)

        return date.date()

def get_free_games():
    games = []
    games_json = requests.get(FREE_GAMES_URL).text
    games_json = json.loads(games_json)['data']['Catalog']['searchStore']['elements']

    for game in games_json:
        if(game['promotions'] is not None):
            if(len(game['promotions']['promotionalOffers']) > 0):
                start_date = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['startDate']

                if(start_date.startswith(str(get_last_new_games_date()))):
                    games.append(Game(game['title'], game['keyImages'][0]['url'], get_game_url(game['title'])))

    return games


def get_rating(game_name):
    '''
    Returns a game object containing the rating of the requested game,
    from the Open Critic API.

    Parameters
    ----------
    game_name - string
        The name of the game to get the rating of.

    Returns
    -------
    Game
        Game object containing the requested game's data and rating.
    '''

    resp = requests.get('https://api.opencritic.com/api/meta/search', params={'criteria': game_name}).text

    if resp != '':
        name = json.loads(resp)[0]['name'].lower().translate(str.maketrans('', '', string.punctuation)) # Extract name and remove punctuation.
        game_name_lower = game_name.lower().translate(str.maketrans('', '', string.punctuation)) # Remove punctuation from user input.

        if name.startswith(game_name_lower):
            game_name = json.loads(resp)[0]['name']
            id = json.loads(resp)[0]['id']

            game_data = json.loads(requests.get('https://api.opencritic.com/api/game/' + str(id)).text)

            # Extract game rating.
            average_score = round(game_data['averageScore'])
            
            # Get game image from bing image search.
            image_search_url = "https://bing-image-search1.p.rapidapi.com/images/search"

            querystring = {'q': game_name, 'count': 1}

            headers = {
                'x-rapidapi-host': 'bing-image-search1.p.rapidapi.com',
                'X-RapidAPI-Key': 'caf6f1e010mshdc9135b118ee85dp109fb2jsn52f824dbb5ef'
            }

            resp = requests.get(image_search_url, headers=headers, params=querystring).text
            image = json.loads(resp)['value'][0]['contentUrl']
            
            # Get game website url from google search.
            params = {
                'engine': 'google',
                'q': game_name,
                'api_key': '10a03c0cf64d5c15db942aacd7b3a194ea91bee5759cc5dbb740540c36aa9ce8',
                'num': 1,
            }

            search = GoogleSearch(params)
            url = search.get_dict()['organic_results'][0]['link']

            return Game(game_name, image, url, average_score)

        else:
            raise GameNotFoundException(game_name)  

    else:
            raise GameNotFoundException(game_name) 


def get_sale(num):
    '''
    Returns a dictionary containing website names as keys and lists of game objects
    as values, where the games are discounted games on each website.

    Parameters
    ----------
    num - int
        The number of discounted games to fetch from each website.

    Returns
    -------
    dict - string, Game
        Dictionary containing website names as keys and lists of game objects as values.
    '''

    resp_dict = {'steam': [], 'origin': [], 'epic': []}
    i = 0

    # Get games on sale on Steam.
    resp = requests.get('https://store.steampowered.com/specials').text
    soup = bs4.BeautifulSoup(resp, 'lxml')
    top_sellers = soup.find(id='TopSellersRows')
    top_sellers = top_sellers.find_all('a')

    for game in top_sellers:
        if i == num:
            break
        name = game.find(class_='tab_item_name').text
        image = game.find('img')['src']
        url = game['href']
        discount_pct = game.find(class_='discount_pct').text
        original_price = game.find(class_='discount_original_price').text
        current_price = game.find(class_='discount_final_price').text

        resp_dict['steam'].append(Game(name, image, url, original_price=original_price, current_price=current_price, discount_pct=discount_pct))
        i += 1    

    return resp_dict

    
def main():
    get_sale()

if __name__ == "__main__":
    main()