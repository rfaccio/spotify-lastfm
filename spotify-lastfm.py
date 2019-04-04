import pylast
import pprint
import json
import sys

import spotipy
import spotipy.util as util

import config
import functions

lastfm_network = pylast.LastFMNetwork(api_key=config.LASTFM_API_KEY,
                                        api_secret=config.LASTFM_API_SECRET,
                                        username=config.LASTFM_USERNAME,
                                        password_hash=pylast.md5(config.LASTFM_PASSWORD))
lastfm_user = lastfm_network.get_authenticated_user()
print(lastfm_user)
#chart_artists = user.get_top_artists(period='7day',limit=3)
#last_loved_tracks = user.get_loved_tracks(limit=5)

rInput = input('Charts ((1) = Overall, (2) = 7 days, (3) = 1 month, (4) = 3 months, (5) = 6 months, (6) = 12 months: ')
periodo = functions.get_periodo(rInput)
qtdBusca = input('Quantidade de musicas a ser retornada: ')
chart_tracks  = lastfm_user.get_top_tracks(period=periodo,limit=int(qtdBusca))

track_ids = []
tracks = []
for i, track in enumerate(chart_tracks):
    t = len(track)
    print(str(i + 1) + ")\t" + str(track[0]))
    tracks.append(str(track[0]))

# track = network.get_track("Stella Donnelly", "Tricks")
# track.love()
# track.add_tags(("awesome", "favorite"))

# Type help(pylast.LastFMNetwork) or help(pylast) in a Python interpreter
# to get more help about anything and see examples of how it works

scope_modify_private = 'playlist-modify-private'
scope_read_private = 'playlist-read-private'
scope_modify_public = 'playlist-modify-public'

scopes = scope_read_private + ' ' + scope_modify_public + ' ' + scope_modify_private
sp_username = input('Usuario spotify: ')

token = util.prompt_for_user_token(sp_username,scopes,client_id=config.SPOTIPY_CLIENT_ID,client_secret=config.SPOTIPY_CLIENT_SECRET,redirect_uri=config.SPOTIPY_REDIRECT_URI)
if not token:
    print('TOKEN = NULL' + token)

try:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    if sys.argv[1] == '1':
        plistInput = input('(1) Criar ou (2) escolher playlist (1/2): ')
        if plistInput == '1':
            pName = input('Nome da playlist :')
            playlists = sp.user_playlist_create(user=sp_username, name=pName, public=False)
            print('playlist ' + pName + ' criada')
            playlist_id = playlists['id']
        elif plistInput == '2':
            playlists = sp.user_playlists(sp_username)
            for i, item in enumerate(playlists['items']):
                print("%d %s" %(i, item['name']))

            pNumber = input("Please choose playlist number: ")
            playlist = playlists['items'][int(pNumber)]
            playlist_id = playlist['id']
        answer = 'y'
        while answer == 'y':
            aName = input('Escolha um artista ou lastfm: ')
            if aName == 'lastfm':
                
                for i, line in enumerate(tracks):
                    try:
                        txt = str(line)
                        print(str(i + 1) + ")\t" + str(txt))
                        (a, t) = functions.split_artist_track(txt)
                        res = sp.search(q='artist: '+ a + ' track: '+t, limit=1, type='track', market='BR')
                        result = res['tracks']['items'][0]
                        track_ids.append(result['id'])
                    except Exception as e:
                        print('\nException:\n')
                        print(e)
                        print('\ntracks:\n')
                        print(tracks)
                answer = 'n'
            else:
                artist = sp.search(q=aName, limit=20)
                for i, t in enumerate(artist['tracks']['items']):
                        print(' ', i, t['name'], t['id'])
                tNumber = input("Choose track number: ")
                track = artist['tracks']['items'][int(tNumber)]
                track_ids.append(track['id'])
                answer = input("Mais? ")

        results = sp.user_playlist_add_tracks(sp_username, playlist_id, track_ids)
        pprint.pprint(results)

    elif sys.argv[1] == '2':
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(sp_username)
        #playlist = playlists['items'][0]
        for i, item in enumerate(playlists['items']):
            print("%d %s" %(i, item['name']))

        pNumber = input("Please choose playlist number: ")
        playlist = playlists['items'][int(pNumber)]
        #playlist_name = playlist['name']
        try:
            results = sp.search(q='Stella Donnelly', limit=20)
            for i, t in enumerate(results['tracks']['items']):
                print(' ', i, t['name'], t['id'])
            tNumber = input("Choose track number: ")
            track = results['tracks']['items'][int(tNumber)]
            track_ids.append(track['id'])
            #playlistz = sp.user_playlist_create(sp_username, 'bot', 'bot desc')
            results = sp.user_playlist_add_tracks(sp_username, playlist['id'], track_ids)            
            pprint.pprint(results)
        except Exception as e:
            print("Can't get token for", sp_username)
            print(e)
    else:
        print("Can't get token for", sp_username)
except Exception as e:
    print(e)