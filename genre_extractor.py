import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pandas as pd
import sys
import requests
import re
import time


def get_artist_genre(sp, spotify_artist_id):
    found_artist = ''
    try:
        artist = sp.artist(spotify_artist_id)
        found_artist = artist['name']
        if len(artist['genres']) != 0:
            # check the artist genre:
            if len(artist['genres']) > 1:
                genres = ', '.join(artist['genres']) 
                return genres
            else:
                return artist['genres'][0]
        else:
            print(f"\nSpotify Doesn't list the Genre(s) for: {found_artist} ")
    except requests.exceptions.ReadTimeout as e:
        print(f'\nAn Error Occured Determining Artist Genre: {e}')
        print(f'\nOccured for Artist: {found_artist}')
    except Exception as e:
        print(f'\nAn Unexpected Error Occurred: {e}')
        print(f'\nOccurred for Artist: {found_artist}')

def get_album_genre(sp, spotify_album_id):
    found_album = ''
    try:
        album = sp.album(spotify_album_id)
        found_album = album['name']
        if len(album['genres']) != 0:
            # check the artist genre:
            if len(album['genres']) > 1:
                genres = ', '.join(album['genres']) 
                return genres
            else:
                return album['genres']
        else:
            print(f"\nSpotify Doesn't list the Genre(s) for Album: {found_album} ")
    except requests.exceptions.ReadTimeout as e:
        print(f'\nAn Error Occured Determining Artist Genre: {e}')
        print(f'\nOccured for Artist: {found_album}')
    except Exception as e:
        print(f'\nAn Unexpected Error Occurred: {e}')
        print(f'\nOccurred for Artist: {found_album}')

def get_album_release_date(sp, spotify_album_id):
    try:
        album = sp.album(spotify_album_id)
        
        return album['release_date']

    except requests.exceptions.ReadTimeout as e:
        print(f'\nAn Error Occured Determining Album Release Date: {e}') 
    except Exception as e:
        print(f'\nAn Unexpected Error Occurred: {e}')


def determine_artist_genre(songs_df, sp_client, username): 
    # identify the unique artists
    artists_album_ids = songs_df['Artist_id']
    # extract the unique artists to prevent duplicate api calls.
    unique_artists = artists_album_ids.unique()

    # create a new dataframe to support the merge later
    artist_genres = pd.DataFrame(unique_artists, columns=['Artist_id'])
    # create a new column to hold the genres
    artist_genres['Artist_Genre'] = None

    artist_count = 1
    for index, artist in enumerate(unique_artists):
        sys.stdout.write(f'\rLoading Artist Genres... {round(((artist_count)/len(unique_artists))*100, 2)}%')
        
        time.sleep(3)
        # per index reference assign the found genre based on the Spotify artist description
        
        artist_genres.loc[index, 'Artist_Genre'] = get_artist_genre(sp_client, artist)
        artist_count += 1
        sys.stdout.flush()


    # There will be several that will not have Genre(s) listed
    # Spotify require a listing of the genre within the Artist profile
    """
        artist_genres shape(,2) with Artist_id, ?Artist_Genre 
        
    """

    # merge the data by id into the existing data_frame
    # only merge the artist genres not the artist_id with how='left'
    songs_df = songs_df.merge(artist_genres, on='Artist_id', how='left')

    print("Waiting 30 seconds before attempting to search the Album_ids")
    time.sleep(30)

    non_genre_listed = artist_genres[artist_genres['Artist_Genre'].isna()]['Artist_id']

    # merge for artists with no listed genre and an album_id
    album_search_for_genre = songs_df.merge(non_genre_listed, on='Artist_id')['Album_id'].unique()

    album_genres = pd.DataFrame(album_search_for_genre, columns=['Album_id'])
    album_genres['Album_Genre'] = None

    album_count = 1
    for index, album in enumerate(album_search_for_genre):
        sys.stdout.write(f'\rLoading Album Genres... {round((album_count)/len(album_search_for_genre)*100, 2)}%')
        
        time.sleep(3)
        # per index reference assign the found genre based on the Spotify artist description
        album_genres.loc[index, 'Album_Genre'] = get_album_genre(sp_client, album)
        album_count += 1
        sys.stdout.flush()
    
    """
        album_genres shape(,2) with Album_id, ?Album_Genre
    """

    # merges the album_genre column into the dataframe
    songs_df = songs_df.merge(album_genres, on='Album_id', how='left')

    # combine both genres this combines the Artist_Genre and Album_Genre columns into a single column Genre
    # combine_first combines the column data choosing the column that has a value.
    # if Artist_Genre is none it will use the Album_Genre
    songs_df['Genre'] = songs_df['Artist_Genre'].combine_first(songs_df['Album_Genre'])

    # Drop the Temp Columns from the Merge
    songs_df.drop(columns=['Artist_Genre', 'Album_Genre'], inplace=True)
    
    songs_df.to_csv(f'{username}_songs_with_artist_genre.csv',index=False)

def determine_albun_release_year(songs_df, sp_client, user_name):
    # aquire unique albums 

    if 'Release_Date' not in songs_df.columns:

        album_ids = songs_df['Album_id'][:1000]

        unique_album_id = album_ids.unique()
        
        # create the dataframe
        artist_albums = pd.DataFrame(unique_album_id, columns=['Album_id'])
        # creates the release date column
        artist_albums['Release_Date'] = None
        
        album_count = 1
        for index, album_id in enumerate(unique_album_id):
            precentage_remaining = round(((album_count)/len(unique_album_id))*100, 2)
            sys.stdout.write(f'\rLoading Album Release Years... {precentage_remaining}%')
            
            artist_albums.loc[index,'Release_Date'] = get_album_release_date(sp_client, album_id) 
            album_count += 1
            
            if index == 1000:
                break

            sys.stdout.flush()

        songs_df = songs_df.merge(artist_albums, on='Album_id', how='left')

        songs_df.to_csv(f'{user_name}_songs_with_album_release_artist_genre.csv', index=False)

    else:

        # create the unique albums that are empty...
        album_ids = songs_df[songs_df['Release_Date'].isnull()][:1000]

        unique_album_id = album_ids['Album_id'].unique()
        
        # create the dataframe
        artist_albums = pd.DataFrame(unique_album_id, columns=['Album_id'])
        # creates the release date column
        artist_albums['Release_Date'] = None
        
        album_count = 1
        for index, album_id in enumerate(unique_album_id):
            precentage_remaining = round(((album_count)/len(unique_album_id))*100, 2)
            sys.stdout.write(f'\rLoading Album Release Years... {precentage_remaining}%')
            
            artist_albums.loc[index,'Release_Date'] = get_album_release_date(sp_client, album_id) 
            album_count += 1
            

            sys.stdout.flush()

        songs_df = songs_df.merge(artist_albums, on='Album_id', how='left', suffixes=('','_new'))

        # Update the Release_Date column with the new values
        songs_df['Release_Date'] = songs_df['Release_Date'].combine_first(songs_df['Release_Date_new'])

        # Drop the temporary Release_Date_new column
        songs_df.drop(columns=['Release_Date_new'], inplace=True)


        songs_df.to_csv(f'{user_name}_songs_with_album_release_artist_genre.csv', index=False)




def main():
    # create spotify clients:

    load_dotenv()

    client_id = os.getenv('APP_CLIENT_ID')

    spotify_app_client_secret = os.getenv("SPOTIFY_APP_CLIENT_SECRET")


    api_sp_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                                                        client_id=client_id,
                                                        client_secret=spotify_app_client_secret,
                                                        ),requests_timeout=30)

    
    current_directory = os.getcwd()

    user_name = ''

    for file in os.listdir(current_directory):
        # create regex.
        liked_tracks_regex = r'_liked_songs_with_artist_details'
        match = re.search(liked_tracks_regex, file)
        if match is not None:
            user_name = match.string[:match.start()]
            file_name = match.string
            # determine the genre with each artist from previous extraction
            artists_details = pd.read_csv(file_name)

            break
    

    ''''
        determines the artist genre from the provided ids to reduce the number 
        of internal calls to the API
    '''

    for file in os.listdir(current_directory):
        album_detail_regex = r'_songs_with_artist_genre'
        match = re.search(album_detail_regex, file)
        if match is not None:
            # check for possible batches that have run previously
            found_batch_file = False
            for file in os.listdir(current_directory):
                album_release_regex = r'_songs_with_album_release_artist_genre.csv'
                album_year_match = re.search(album_release_regex, file)
                if album_year_match is not None:
                    found_batch_file = True
                    file_name = album_year_match.string
                    album_details = pd.read_csv(file_name)
                    break

            if found_batch_file == False:
                file_name = match.string
                album_details = pd.read_csv(file_name)
                break
            else: 
                break
        

    

    determine_albun_release_year(songs_df=album_details, sp_client=api_sp_client, user_name=user_name)


main()