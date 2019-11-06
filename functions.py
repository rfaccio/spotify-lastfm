import sys
import config
import getpass

import pylast
import spotipy
import spotipy.util as util

#lastfm chart options
PERIOD_OVERALL = "overall"
PERIOD_7DAYS = "7day"
PERIOD_1MONTH = "1month"
PERIOD_3MONTHS = "3month"
PERIOD_6MONTHS = "6month"
PERIOD_12MONTHS = "12month"

def init_lastfm(lastfm_username=None,lastfm_password=None):
    if not config.LASTFM_USERNAME:
        config.LASTFM_USERNAME = input('Lastfm username: ')
    if not config.LASTFM_USERNAME:        
        config.LASTFM_PASSWORD = getpass.getpass('Lastfm password: ')
    try:
        return pylast.LastFMNetwork(api_key=config.LASTFM_API_KEY,
                                    api_secret=config.LASTFM_API_SECRET,
                                    username=config.LASTFM_USERNAME,
                                    password_hash=pylast.md5(config.LASTFM_PASSWORD))
    except Exception as e:
        print(e)

def init_spotipy(username):
    scope_modify_private = 'playlist-modify-private'
    scope_read_private = 'playlist-read-private'
    scope_modify_public = 'playlist-modify-public'

    scopes = scope_read_private + ' ' + scope_modify_public + ' ' + scope_modify_private
    if username != None:
        sp_username = username
    else:
        sp_username = input('Usuario spotify: ')

    try:
        token = util.prompt_for_user_token(sp_username,scopes,client_id=config.SPOTIPY_CLIENT_ID,client_secret=config.SPOTIPY_CLIENT_SECRET,redirect_uri=config.SPOTIPY_REDIRECT_URI)
        if token:
            return token, sp_username
    except Exception as e:
        print(e)

def split_artist_track(artist_track):
    artist_track = artist_track.replace(" – ", " - ")
    artist_track = artist_track.replace("“", '"')
    artist_track = artist_track.replace("”", '"')

    (artist, track) = artist_track.split(' - ', 1)
    artist = artist.strip()
    track = track.strip()
    # Validate
    if len(artist) is 0 and len(track) is 0:
        sys.exit("Error: Artist and track are blank")
    if len(artist) is 0:
        sys.exit("Error: Artist is blank")
    if len(track) is 0:
        sys.exit("Error: Track is blank")

    return (artist, track)

def get_periodo(rInput=1):
    if rInput == '1':
        return PERIOD_OVERALL
    elif rInput == '2':
        return PERIOD_7DAYS
    elif rInput == '3':
        return PERIOD_1MONTH
    elif rInput == '4':
        return PERIOD_3MONTHS
    elif rInput == '5':
        return PERIOD_6MONTHS
    elif rInput == '6':
        return PERIOD_12MONTHS
    else:
        return PERIOD_OVERALL