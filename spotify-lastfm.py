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
    plistInput = input('Criar [1] ou Escolher Playlist [2]: ')
    if plistInput == '1': #cria playlist nova
        pName = input('Nome da playlist :')
        playlists = spotipy.user_playlist_create(user=sp_username, name=pName, public=False)
        print('playlist ' + pName + ' criada')
        playlist_id = playlists['id']
    elif plistInput == '2': #exibe playlists do usuario para seleção
        offset = 1
        all_playlists = []
        while True:
            playlists = spotipy.user_playlists(sp_username, offset=offset)
            for i, item in enumerate(playlists['items']):
                #print("%d %s" %(i, item['name']))
                offset = offset + i
                all_playlists.append(item)
            if len(playlists['items']) == 0:
                break
        for i, item in enumerate(all_playlists):
            print("%d %s" %(i, item['name']))

        pNumber = input("Please choose playlist number: ")
        playlist = all_playlists[int(pNumber)]
        playlist_id = playlist['id']

    #inicializa variavel answer
    answer = 's'
    track_ids = []
    tracks = []
    while answer == 's':

        aName = input('Digite uma busca, ou "lastfm"/"file"/"feed": ')
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
            arquivo = open(filepath, 'r', encoding='utf-8')
            track_ids, not_found = functions.search_song(spotipy, arquivo)

        elif aName == 'feed':
            if not feed:
                feedUrl = input('URL do feed do podcast: ')
                feed = feedparser.parse(feedUrl)

            for entry in feed.entries:
                print('\n---------')
                print('Feed: ', entry.title, ':')
                
                try:
                    if os.path.isfile('feed/' + entry.title + '.txt'):
                        print('> Feed já foi lido')
                        continue
                    else:
                        print('---------\n')
                        arq = open('feed/' + entry.title + '.txt', 'w', encoding='utf-8')
                        arq.write(entry.summary)
                        arq.close()

                    arq = open('feed/' + entry.title + '.txt', 'r', encoding='utf-8')
                except Exception as e:
                    print(e)
                    continue

                track_ids, not_found = functions.search_song(spotipy, arq)
                if len(track_ids) > 0:
                    results = spotipy.user_playlist_add_tracks(sp_username, playlist_id, track_ids)
                    print(len(track_ids), ' tracks added to: ', playlist['name'])
                    track_ids = []
                if len(not_found) > 0:
                    arq_not_found = open('feed/' + 'not_found.txt', 'a', encoding='utf-8')
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
    print(len(track_ids), ' tracks added to: ', playlist['name'])
    pprint.pprint(results)
except Exception as e:
    print(e)


#chart_artists = user.get_top_artists(period='7day',limit=3)
#last_loved_tracks = user.get_loved_tracks(limit=5)


# track = network.get_track("Stella Donnelly", "Tricks")
# track.love()
# track.add_tags(("awesome", "favorite"))