# NOTES:
# it might be easier to write my own parser. python-lichess does it themselves, using these lines of code:
# https://github.com/cyanfish/python-lichess/blob/8deea5dda8965b90915c744d65f2a4bc3ee085e5/lichess/api.py#L293
# https://github.com/cyanfish/python-lichess/blob/8deea5dda8965b90915c744d65f2a4bc3ee085e5/lichess/api.py#L89
# there's something with specifying the object_type=lichess.format.GAME_STREAM_OBJECT and passing it to the parser

# RESOURCES
# https://devcenter.heroku.com/articles/flask-memcache
# https://lichess.org/api#operation/apiUserCurrentGame

import pandas as pd
import re
import lichess.api
import logging
import json
import datetime as dt
import requests
from flask import Flask

app = Flask(__name__)
logger = app.logger
logger.setLevel(logging.INFO)
MAX_LICHESS_GAMES = 500
SECONDS_PER_DAY = 24 * 60 * 60

def process_lichess_game_dict(game_dict, username):
    """
    Processes a single game dictionary, as it comes from the result of `lichess.api.user_games()`.
    """

    # get opening info
    opening_name = game_dict["opening"]["name"]
    opening_name_simple = opening_name.split(':')[0]
    opening_code = game_dict["opening"]["eco"]

    # get color
    if 'aiLevel' in game_dict["players"]["white"].keys():
        color = "black"
    elif 'aiLevel' in game_dict["players"]["black"].keys():
        color = "white"
    elif game_dict["players"]["white"]["user"]["name"]==username:
        color = "white"
    else:
        color = "black"

    # get points
    if "winner" not in game_dict:
        points = .5
    elif game_dict["winner"]==color:
        points = 1
    else:
        points = 0

    # return
    return {"opening_name": opening_name,
            "opening_name_simple": opening_name_simple,
            "opening_code": opening_code, 
            "color": color,
            "points": points}

def process_chesscom_game_dict(game_dict, username):

    # take the game pgn
    pgn = game_dict['pgn']

    # get opening info
    opening_name_pattern = r'\[ECOUrl "https:\/\/www\.chess\.com\/openings\/([\d\.a-zA-Z-]+)"]'
    opening_code_pattern = r'\[ECO "([A-Z]{1}\d{2})"]'
    opening_name = re.findall(opening_name_pattern, pgn)[0].replace('-', ' ')
    opening_name_simple = " ".join(opening_name.split(' ', 2)[:2])
    opening_code = re.findall(opening_code_pattern, pgn)[0]

    # get color info
    if game_dict["white"]["username"]==username:
        color = "white"
    elif game_dict["black"]["username"]==username:
        color = "black"
    else:
        logger.error('error in getting game color')

    # get points info
    # TODO figure out if it's a draw or not!
    points = 1 if game_dict[color]["result"]=="win" else 0    

    # return
    return {"opening_name": opening_name,
            "opening_name_simple": opening_name_simple,
            "opening_code": opening_code,
            "color": color,
            "points": points}

def is_legal_chesscom_game(game_dict):
    """
    Not all games have all requisite data. If they don't, return False; else, return True.
    """
    opening_name_pattern = r'\[ECOUrl "https:\/\/www\.chess\.com\/openings\/([\d\.a-zA-Z-]+)"]'
    if len(re.findall(opening_name_pattern, game_dict['pgn']))==1:
        return True
    return False

def is_legal_lichess_game(game_dict):
    """
    Not all games have all requisite data. If they don't, return False; else, return True.
    """
    if "opening" in game_dict:
        return True
    return False

def is_lichess_user(lichess_username):
    """
    Check if a user exists on lichess.
    """
    try:
        user = lichess.api.user(lichess_username)
        return True
    except lichess.api.ApiHttpError:
        return False

def is_chesscom_user(chesscom_username):
    player_dict = json.loads(requests.get(f"https://api.chess.com/pub/player/{chesscom_username}").content)
    if "player_id" in player_dict:
        return True
    return False

def get_lichess_user_games_df(lichess_username, num_lookback_days):
    """
    Get all the formatted lichess gamese of a lichess user.

    Note on the maximum speed of this function
    (from https://lichess.org/api#operation/apiGamesUser):
        "The game stream is throttled, depending on who is making the request:
            - Anonymous request: 20 games per second
            - OAuth2 authenticated request: 30 games per second
            - Authenticated, downloading your own games: 60 games per second"
    """
    since = 1000 * (int(dt.datetime.utcnow().timestamp()) - num_lookback_days * SECONDS_PER_DAY)
    logger.info(num_lookback_days)
    logger.info(since)
    query = {
        "opening": True,
        "moves": False,
        "sort": "dateDesc",
        "since": since,
        "max": MAX_LICHESS_GAMES}
    games = [process_lichess_game_dict(g, lichess_username)
            for g in lichess.api.user_games(lichess_username, **query)
            if is_legal_lichess_game(g)]
    df = pd.DataFrame(games)
    df["website"] = "lichess"
    return df

def get_chesscom_user_games_df(chesscom_username, num_lookback_days):
    """
    Get all the formatted chess.com games of a chess.com user.

    Notes on the chess.com public API:
        To get past games from the chess.com api, there is a some month-wise archived folder endpoint.
        Then, we'll have to hit a different endpoint to get the games of each month, since not every month
        necessarily has games:
        https://api.chess.com/pub/player/normanrookwell/games/archives
        https://api.chess.com/pub/player/normanrookwell/games/2021/10
    """


    # get the query month range.
    # TODO: fix the hokey-ness forced by pd.date_range function
    dates = pd.date_range(dt.date.today() - dt.timedelta(days=num_lookback_days),
                          dt.date.today() + dt.timedelta(days=30),
                          freq="M")
    
    # get all the games from all the months
    games = [process_chesscom_game_dict(game, chesscom_username)
             for date in dates
             for game in get_chesscom_user_month_games(chesscom_username, date.year, date.month)
             if is_legal_chesscom_game(game)]
    
    # return
    df = pd.DataFrame(games)
    df["website"] = "chessdotcom"
    return df

def get_user_opening_stats(chess_username: str, num_lookback_days=100, platform="lichess"):
    """
    Get the opening statistics of a given user.

    Returns a 2-tuple (pd.DataFrame of white opening stats, pd.DataFrame of black opening stats)
    """
    if platform=="lichess":
        games_df = get_lichess_user_games_df(chess_username, num_lookback_days)
    if platform=="chesscom":
        games_df = get_chesscom_user_games_df(chess_username, num_lookback_days)
    if platform=="both":
        games_df = pd.concat([get_chesscom_user_games_df(chess_username, num_lookback_days),
                              get_lichess_user_games_df(chess_username, num_lookback_days)])
    opening_stats = {
        color: (games_df
                [games_df["color"]==color]
                .groupby("opening_name_simple")
                ["points"]
                .agg(["count", "mean"])
                .sort_values("count", ascending=False)
                .head(5)
                .reset_index()
                .rename({"opening_name_simple": "opening",
                         "count": "num_games",
                         "mean": "avg_points_per_game"},
                        axis=1)
                .to_dict("records"))
        for color in ["white", "black"]}
    return opening_stats

def get_chesscom_user_month_games(chesscom_username, year, month):
    """
    Get the games for a chesscom user for one month:

    https://api.chess.com/pub/player/normanrookwell/games/2021/10
    """
    url = f"https://api.chess.com/pub/player/{chesscom_username}/games/{year}/{month:02d}"
    return json.loads(requests.get(url).content)['games']

# main
if __name__=="__main__":

    # test name
    test_names = [
        "nikolaserdmann",
        "normanrookwell",
        "KorayKayir",
        "madmaxmatze"
    ]
    for name in test_names:
        print(get_user_opening_stats(chess_username="nikolaserdmann", num_games=100, num_lookback_days=200, platform="both"))
