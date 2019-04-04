import sys

#lastfm chart options
PERIOD_OVERALL = "overall"
PERIOD_7DAYS = "7day"
PERIOD_1MONTH = "1month"
PERIOD_3MONTHS = "3month"
PERIOD_6MONTHS = "6month"
PERIOD_12MONTHS = "12month"

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