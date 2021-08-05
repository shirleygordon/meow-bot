import requests
import json
import datetime
import string
from serpapi import GoogleSearch


FREE_GAMES_URL = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=IL&allowCountries=IL'
GAME_URL = 'https://www.epicgames.com/store/en-US/p/'
THURSDAY = 3
WEDNESDAY = 2

class Game:
    def __init__(self, name, image, url='', rating=None):
        self._name = name
        self._image = image

        if url == '':
            self._url = get_game_url(name)
        else:
            self._url = url
            
        self._rating = rating

    def get_name(self):
        return self._name

    def get_image(self):
        return self._image

    def get_url(self):
        return self._url

    def get_rating(self):
        return self._rating


class GameNotFoundException(Exception):
    def __init__(self, game_name):
        super().__init__('meow! the game "{}" was not found. :('.format(game_name))


def get_game_url(name):
    return GAME_URL + name.lower().replace(' ', '-')

def get_last_new_games_date():
    todays_date = datetime.datetime.now()

    if todays_date.weekday() == THURSDAY and todays_date.hour > 18:
            return datetime.date.today()

    else:
        date = datetime.datetime.today()

        if date.weekday() == THURSDAY:
            date -= datetime.timedelta(days=1)

        while date.weekday() != THURSDAY:            
            date -= datetime.timedelta(days=1)
        return date.date()

def get_free_games():
    games = []
    games_json = requests.get(FREE_GAMES_URL).text
    games_json = json.loads(games_json)['data']['Catalog']['searchStore']['elements']

    for game in games_json:
        if game['effectiveDate'].startswith(str(get_last_new_games_date())):
            games.append(Game(game['title'], game['keyImages'][0]['url']))

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

    
def main():
    get_rating('fortnite')

if __name__ == "__main__":
    main()