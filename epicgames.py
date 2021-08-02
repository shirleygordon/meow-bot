import requests
import json
import datetime

FREE_GAMES_URL = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=IL&allowCountries=IL'
GAME_URL = 'https://www.epicgames.com/store/en-US/p/'
THURSDAY = 3
WEDNESDAY = 2

class Game:
    def __init__(self, name, image):
        self._name = name
        self._image = image
        self._url = get_game_url(name)

    def get_name(self):
        return self._name

    def get_image(self):
        return self._image

    def get_url(self):
        return self._url

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
    
def main():
    get_free_games()

if __name__ == "__main__":
    main()