import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import pandas as pd
import sys
import requests
import time


def checkConnection(sp):
    try:
        # check connection 
        gorillaz_uri = 'spotify:artist:3AA28KZvwAUcZuOKwyblJQ'

        results = sp.artist_albums(gorillaz_uri, album_type='album')
        albums = results['items']
        
        print("Connection Succesfull:")

        print("Gorillaz Albums:")
        print("----------------------------------")

        while results['next']:
            results = sp.next(results)
            albums.extend(results['items'])

        for album in albums:
            print(album['name'])
    except Exception as e:
        print(f"Something went wrong with Spotify Authorization: {e}")

def get_artists(artists_list):
    artists = ''
    
    if len(artists_list) == 1:
        artists += artists_list[0]['name']
        return artists
    
    else:
        
        for i in range(len(artists_list)):
            artist_name = artists_list[i]['name']
            if i == len(artists_list) - 1:
                if artist_name not in artists:
                    artists += artist_name 
            else:
                artists += artist_name  + ', '

        
    return artists


def parse_tracks(sp, saved_track_data, saved_tracks):

    for i in range(len(saved_tracks)):
        song_name = saved_tracks[i]['track']['name']
        
        length = calc_duration_ms(saved_tracks[i]['track']['duration_ms'])
        
        album_name = saved_tracks[i]['track']['album']['name']
        
        artists = get_artists(saved_tracks[i]['track']['artists'])
        
        song_artist_url = saved_tracks[i]['track']['artists'][0]['external_urls']['spotify']
        
        album_url = saved_tracks[i]['track']['album']['external_urls']['spotify']
        
        time.sleep(30)
        genres = get_artist_genre(sp, song_artist_url, album_url)

        time.sleep(30)
        release_date = get_album_release_year(sp, album_url)

        # adds the song details into dictionary
        saved_track_data['Song Name'].append(song_name)
        
        saved_track_data['Duration'].append(length)
        
        saved_track_data['Album'].append(album_name)
        
        saved_track_data['Artists'].append(artists)
        
        saved_track_data['Genre'].append(genres)

        saved_track_data['Release Date'].append(release_date)
        
    

def calc_duration_ms(duration_ms):
    minute_conversion = duration_ms / 1000 / 60
    minute_total = round(minute_conversion, 2)
    return str(minute_total).replace('.',':')

def get_artist_genre(sp, spotify_external_url, spotify_album_url):
    found_artist = ''
    try:
        artist = sp.artist(spotify_external_url)
        time.sleep(10)
        found_artist = artist['name']
        if len(artist['genres']) == 0:
            # check the album genre:
            album = sp.album(spotify_album_url)
            return album['genres']
        else:
            return artist['genres']
    except requests.exceptions.ReadTimeout as e:
        print(f'\nAn Error Occured Determining Artist Genre: {e}')
        print(f'\nOccured for Artist: {found_artist}')
    except Exception as e:
        print(f'\nAn Unexpected Error Occurred: {e}')
        print(f'\nOccurred for Artist: {found_artist}')

def get_album_release_year(sp, spotify_external_url):
    found_album = ''
    try: 
        album = sp.album(spotify_external_url)
        found_album = album['name']
        return album['release_date']
    except requests.exceptions.ReadTimeout as e:
        print(f'\nAn Error Occurred Retrieving Album Year: {e}')
        print(f'\nOccured for Album: {found_album}')
    except Exception as e:
        print(f'\nAn Unexpected Error Occurred: {e}')
        print(f'\nOccurred for Album: {found_album}')

    

def export_track_data(saved_tracks, user_name):
    df = pd.DataFrame(saved_tracks)

    file_name = user_name + '_liked_songs.csv'

    df.to_csv(file_name, index=False)

def main():
    # load the client variables
    load_dotenv()

    client_id = os.getenv('APP_CLIENT_ID')

    spotify_app_client_secret = os.getenv("SPOTIFY_APP_CLIENT_SECRET")

    spotify_app_redirect = os.getenv("SPOTIFY_APP_REDIRECT_URI")


    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=spotify_app_client_secret,
                                                redirect_uri=spotify_app_redirect,
                                                scope=["user-library-read","playlist-modify-private"]))

    results = sp.current_user_saved_tracks()
    
    current_user = sp.current_user()
    
    print('Current User Details:' )
    print('-------------------------------------------')
    print(f'User Name: {current_user['display_name']}' )
    print(f'Total Liked Songs: {results['total']}')

    total_num_saved = results['total']

    saved_tracks_data = {
        'Song Name': [],
        'Duration': [],
        'Album': [],
        'Artists': [],
        'Genre':[], 
        'Release Date': [],

    }

    offset_index = 0

    while offset_index != total_num_saved:
        results = sp.current_user_saved_tracks(limit=50, offset=offset_index)
        
        total_saved_tracks = results['items']

        sys.stdout.write(f'\rLoading Song Data... {round(((offset_index+50)/total_num_saved)*100)}%')
        
        parse_tracks(sp=sp, saved_track_data=saved_tracks_data, saved_tracks=total_saved_tracks)
        time.sleep(20)
        
        sys.stdout.flush()

        # control offset increase:
        if (offset_index + 50) < total_num_saved:
            offset_index += 50
        else:
            # determine the difference to offset
            if (offset_index + 20) > total_num_saved:
                offset_index = (total_num_saved - offset_index) + offset_index


    print('\n--------------------------------')
    print('\nExporting Complete!')
    print('--------------------------------')
    print('Exporting Liked Songs')
    user_name = current_user['display_name'].replace(' ', '_')
    export_track_data(saved_tracks=saved_tracks_data, user_name=user_name )
    


main()