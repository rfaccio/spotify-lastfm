import pylast
import pprint
import json
import sys
import spotipy
import spotipy.util as util
import feedparser
import config
import functions
import os

username = None
if len(sys.argv) > 1:
    username = sys.argv[1]

#realiza a autenticação nas APIs
lastfm_network = functions.init_lastfm()
token, sp_username = functions.init_spotipy(username)
spotipy = spotipy.Spotify(auth=token)
if sp_username == '':
    sp_username = spotipy.current_user()['id']
feed = feedparser.parse('http://feeds.feedburner.com/ReverberationRadio')

try:
    spotipy.trace = False
    plistInput = input('(1) Criar ou (2) escolher playlist (1/2): ')
    if plistInput == '1': #cria playlist nova
        pName = input('Nome da playlist :')
        playlists = spotipy.user_playlist_create(user=sp_username, name=pName, public=False)
        print('playlist ' + pName + ' criada')
        playlist_id = playlists['id']
    elif plistInput == '2': #exibe playlists do usuario para seleção
        playlists = spotipy.user_playlists(sp_username)
        for i, item in enumerate(playlists['items']):
            print("%d %s" %(i, item['name']))

        pNumber = input("Please choose playlist number: ")
        playlist = playlists['items'][int(pNumber)]
        playlist_id = playlist['id']

    #inicializa variavel answer
    answer = 's'
    track_ids = []
    tracks = []
    while answer == 's':

        aName = input('Escolha um artista ou lastfm: ')
        if aName == 'lastfm': #se escolher lastfm, adiciona na playlists as listas de mais tocadas
            
            lastfm_user = lastfm_network.get_authenticated_user()
            print(str(lastfm_user) + ' autenticado')

            rInput = input('Top Charts: \n(1) = Overall, (2) = 7 days, (3) = 1 month, (4) = 3 months, (5) = 6 months, (6) = 12 months: ')
            periodo = functions.get_periodo(rInput)
            qtdBusca = input('Quantidade de musicas: ')
            chart_tracks  = lastfm_user.get_top_tracks(period=periodo,limit=int(qtdBusca))

            #lista as musicas mais tocadas no período
            for i, track in enumerate(chart_tracks):
                t = len(track)
                print(str(i + 1) + ")\t" + str(track[0]))
                tracks.append(str(track[0]))

            if input('Adicionar esta lista? (s/n)') == 's':
                for i, line in enumerate(tracks):
                    try:
                        txt = str(line)
                        print(str(i + 1) + ")\t" + str(txt)) + ' adicionada.'
                        (a, t) = functions.split_artist_track(txt)
                        res = spotipy.search(q='artist: '+ a + ' track: '+t, limit=1, type='track', market='BR')
                        result = res['tracks']['items'][0]
                        track_ids.append(result['id'])
                    except Exception as e:
                        print('\nException:\n')
                        print(e)
                        print('\ntracks:\n')
                        print(tracks)
        elif aName == 'file':
            filepath = input('Caminho do arquivo: ')
            arquivo = open(filepath, 'r')
            lista = []
            for line in arquivo:
                line = line.split('. ')[1]
                (a, t) = functions.split_artist_track(line)
                result = spotipy.search(q='artist: '+ a + ' track: '+t, limit=1, type='track', market='BR')
                if len(result['tracks']['items']) == 0:
                    result = spotipy.search(q=line, limit=1)
                    if len(result['tracks']['items']) == 0:
                        result = spotipy.search(q='track: '+t, limit=1)
                        if len(result['tracks']['items']) == 0:
                            print(a, ' - ', t, ': not found.')
                        else:
                            track_ids.append(result['tracks']['items'][0]['id'])
                            print(a, ' - ', t, ': added.')
                    else:
                        track_ids.append(result['tracks']['items'][0]['id'])
                        print(a, ' - ', t, ': added.')
                else:
                    track_ids.append(result['tracks']['items'][0]['id'])
                    print(a, ' - ', t, ': added.')
        elif aName == 'feed':
            
            for entry in feed.entries:
                not_found = []
                print('\n---------')
                print('Feed: ', entry.title, ':')
                
                if os.path.isfile(entry.title + '.txt'):
                    print('> Feed já foi lido')
                    continue
                #if input('Save entry %s in spotify? (s/n) > ' % entry.title) == 'n':
                #    break
                print('---------\n')
                arq = open(entry.title + '.txt', 'w', encoding='utf-8')
                arq.write(entry.summary)
                arq.close()
                
                arq = open(entry.title + '.txt', 'r', encoding='utf-8')
                for line in arq:
                    if not line[0].isdigit():
                        continue
                    song = line.split('. ', 1)[1]
                    song = song.replace(" – ", " - ")
                    if '-' not in song:
                        continue
                    (a, t) = functions.split_artist_track(song)
                    result = spotipy.search(q='artist: '+ a + ' track: '+t, limit=1, type='track', market='BR')
                    if len(result['tracks']['items']) == 0:
                        result = spotipy.search(q=song, limit=1, type='track')
                        if len(result['tracks']['items']) == 0:
                            result = spotipy.search(q='track: '+t, limit=20, type='track')
                            if len(result['tracks']['items']) == 0:
                                not_found.append(line)
                                print(a, ' - ', t, ': not found.')
                            else:
                                msg_t3 = a + ' - ' + t + ': not found.'
                                for i in result['tracks']['items']:
                                    for nome in i['artists']:
                                        if nome['name'] in a:
                                            track_ids.append(i['id'])
                                            msg_t3 = a + ' - ' + t + ': added.'
                                            break                                
                                if 'not found' in msg_t3:
                                    not_found.append(line)
                                print(msg_t3)
                        else:
                            track_ids.append(result['tracks']['items'][0]['id'])
                            print(a, ' - ', t, ': added.')
                    else:
                        track_ids.append(result['tracks']['items'][0]['id'])
                        print(a, ' - ', t, ': added.')
                if len(track_ids) > 0:
                    results = spotipy.user_playlist_add_tracks(sp_username, playlist_id, track_ids)
                    track_ids = []
                if len(not_found) > 0:
                    arq_not_found = open('not_found.txt', 'a', encoding='utf-8')
                    for line in not_found:
                        arq_not_found.write(line)
                    arq_not_found.close()
        else:
            artist = spotipy.search(q=aName, limit=20)
            if len(artist['tracks']['items']) == 0:
                print('Nenhum resultado encontrado para: ', aName)
            else:
                for i, t in enumerate(artist['tracks']['items']):
                    print(' ', i, t['artists'][0]['name'], ' - ', t['name'])
                
                tNumber = input("Escolha a musica: ")
                track = artist['tracks']['items'][int(tNumber)]
                track_ids.append(track['id'])
        answer = input("Mais? (s/n) > ")

    results = spotipy.user_playlist_add_tracks(sp_username, playlist_id, track_ids)
    pprint.pprint(results)
except Exception as e:
    print(e)


#chart_artists = user.get_top_artists(period='7day',limit=3)
#last_loved_tracks = user.get_loved_tracks(limit=5)


# track = network.get_track("Stella Donnelly", "Tricks")
# track.love()
# track.add_tags(("awesome", "favorite"))