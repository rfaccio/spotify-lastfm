import pylast
import pprint
import json
import sys
import getpass
import spotipy
import spotipy.util as util

import config
import functions

lastfm_network = functions.init_lastfm()
token, sp_username = functions.init_spotipy()
spotipy = spotipy.Spotify(auth=token)

try:
    spotipy.trace = False
    plistInput = input('(1) Criar ou (2) escolher playlist (1/2): ')
    if plistInput == '1':
        pName = input('Nome da playlist :')
        playlists = spotipy.user_playlist_create(user=sp_username, name=pName, public=False)
        print('playlist ' + pName + ' criada')
        playlist_id = playlists['id']
    elif plistInput == '2':
        playlists = spotipy.user_playlists(sp_username)
        for i, item in enumerate(playlists['items']):
            print("%d %s" %(i, item['name']))

        pNumber = input("Please choose playlist number: ")
        playlist = playlists['items'][int(pNumber)]
        playlist_id = playlist['id']

    answer = 'y'
    while answer == 'y':
        track_ids = []
        tracks = []

        aName = input('Escolha um artista ou lastfm: ')
        if aName == 'lastfm':
            
            lastfm_user = lastfm_network.get_authenticated_user()
            print(str(lastfm_user) + ' autenticado')

            rInput = input('Charts (1) = Overall, (2) = 7 days, (3) = 1 month, (4) = 3 months, (5) = 6 months, (6) = 12 months: ')
            periodo = functions.get_periodo(rInput)
            qtdBusca = input('Quantidade de musicas: ')
            chart_tracks  = lastfm_user.get_top_tracks(period=periodo,limit=int(qtdBusca))

            for i, track in enumerate(chart_tracks):
                t = len(track)
                print(str(i + 1) + ")\t" + str(track[0]))
                tracks.append(str(track[0]))

            for i, line in enumerate(tracks):
                try:
                    txt = str(line)
                    print(str(i + 1) + ")\t" + str(txt))
                    (a, t) = functions.split_artist_track(txt)
                    res = spotipy.search(q='artist: '+ a + ' track: '+t, limit=1, type='track', market='BR')
                    result = res['tracks']['items'][0]
                    track_ids.append(result['id'])
                except Exception as e:
                    print('\nException:\n')
                    print(e)
                    print('\ntracks:\n')
                    print(tracks)

            answer = 'n'
        else:
            artist = spotipy.search(q=aName, limit=20)

            for i, t in enumerate(artist['tracks']['items']):
                    print(' ', i, t['name'])

            tNumber = input("Choose track number: ")
            track = artist['tracks']['items'][int(tNumber)]
            track_ids.append(track['id'])
            answer = input("Mais? ")

    results = spotipy.user_playlist_add_tracks(sp_username, playlist_id, track_ids)
    pprint.pprint(results)
except Exception as e:
    print(e)


#chart_artists = user.get_top_artists(period='7day',limit=3)
#last_loved_tracks = user.get_loved_tracks(limit=5)


# track = network.get_track("Stella Donnelly", "Tricks")
# track.love()
# track.add_tags(("awesome", "favorite"))