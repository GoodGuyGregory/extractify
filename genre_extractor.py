import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pandas as pd
import sys
import requests
import re


def get_artist_genre(sp, spotify_artist_id):
    found_artist = ''
    try:
        artist = sp.artist(spotify_artist_id)
        found_artist = artist['name']
        if len(artist['genres']) != 0:
            # check the artist genre:
            return artist['genres']
        else:
            print(f"Spotify Doesn't list the Genre(s) for: {found_artist} ")
    except requests.exceptions.ReadTimeout as e:
        print(f'\nAn Error Occured Determining Artist Genre: {e}')
        print(f'\nOccured for Artist: {found_artist}')
    except Exception as e:
        print(f'\nAn Unexpected Error Occurred: {e}')
        print(f'\nOccurred for Artist: {found_artist}')


def determine_artist_genre(songs_df, sp_client, username): 
    # identify the unique artists
    artists = songs_df['Artist_id']
    # extract the unique artists to prevent duplicate api calls.
    unique_artists = artists.unique()

    artist_count = 1
    for artist in unique_artists:
        sys.stdout.write(f'\rLoading Song Genres... {round(((artist_count)/len(unique_artists))*100)}%')
        unique_artists['Artist_Genre'] = get_artist_genre(sp_client, artist)
        artist_count += 1
        sys.stdout.flush()

    # merge the data by id into the existing data_frame
    Artists_With_Genres = songs_df.merge(unique_artists, right_on='Artist_id')
    Artists_With_Genres.to_csv(f'{username}_songs_with_artist_genre.csv',index=False)

def main():
    # create spotify clients:

    load_dotenv()

    client_id = os.getenv('APP_CLIENT_ID')

    spotify_app_client_secret = os.getenv("SPOTIFY_APP_CLIENT_SECRET")


    api_sp_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                                                        client_id=client_id,
                                                        client_secret=spotify_app_client_secret,
                                                        ),requests_timeout=30)

    
    # determine the genre with each artist
    artists_details = pd.read_csv('Greg_Witt_liked_songs.csv')

    ''''
        determines the artist genre from the provided ids to reduce the number 
        of internal calls to the API
    '''

    current_directory = os.getcwd()

    for file in os.listdir(current_directory):
        # create regex.
        liked_tracks_regex = r'_liked_songs'
        match = re.search(liked_tracks_regex, file)
        if match is not None:
            user_name = match.string[:match.start()]
            break
    


    determine_artist_genre(songs_df=artists_details, sp_client=api_sp_client, username=)



main()