import random
import requests


def get_random_league_champion():
    response =  requests.get('https://ddragon.leagueoflegends.com/cdn/15.21.1/data/en_US/champion.json')

    if response.status_code != 200:
        raise Exception("Error obtaining a league champion.")
    
    json_response = response.json()
    champions =  json_response["data"]

    if not champions:
        raise Exception("Error obtaining a league champion")

    random_choice = random.randint(1, len(champions))
    random_champion = list(champions.keys())[random_choice]

    if not random_champion:
        raise Exception("Error obtaining a random league champion")
    
    return random_champion
