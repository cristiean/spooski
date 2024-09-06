import csv
import os
import requests

# Retrieve client_id and client_secret from environment variables
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
# USER_ID = os.getenv('USER_ID')
# PLAYLIST_ID = os.getenv('PLAYLIST_ID')

def get_access_token():
    # Define the token URL and the necessary data
    url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the POST request to get the access token
    response = requests.post(url, headers=headers, data=data)

    # Check if the request was successful and print the token
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        print('Failed to retrieve token:', response.status_code, response.text)
        return None


def get_user_playlists(user_id):
    # Define the access token
    access_token = get_access_token() # Replace with your actual token

    # Define the URL and the authorization header
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the GET request to retrieve the user's playlist information
    response = requests.get(url, headers=headers)

    # Check if the request was successful and print the user's playlist information
    if response.status_code == 200:
        # return response.json()
        return response.content
    else:
        print('Failed to retrieve user\'s playlist information info:', response.status_code, response.text)
        return None

def get_playlist(playlist_id):
    # Define the access token
    access_token = get_access_token() # Replace with your actual token

    # Define the URL and the authorization header
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the GET request to retrieve the user's playlist information
    response = requests.get(url, headers=headers)

    # Check if the request was successful and print the user's playlist information
    if response.status_code == 200:
        return response.json()
        # return response.content
    else:
        print('Failed to retrieve playlist information info:', response.status_code, response.text)
        return []


def get_track_audio_features(track_id):
    # Define the access token
    access_token = get_access_token() # Replace with your actual token

    # Define the URL and the authorization header
    url = f'https://api.spotify.com/v1/audio-features/{track_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the GET request to retrieve the user's playlist information
    response = requests.get(url, headers=headers)

    # Check if the request was successful and print the user's playlist information
    if response.status_code == 200:
        return response.json()
        # return response.content
    else:
        print('Failed to retrieve track audio features:', response.status_code, response.text)
        return None


def get_track_audio_analysis(track_id):
    # Define the access token
    access_token = get_access_token() # Replace with your actual token

    # Define the URL and the authorization header
    url = f'https://api.spotify.com/v1/audio-analysis/{track_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the GET request to retrieve the user's playlist information
    response = requests.get(url, headers=headers)

    # Check if the request was successful and print the user's playlist information
    if response.status_code == 200:
        return response.json()
        # return response.content
    else:
        print('Failed to retrieve track audio analysis:', response.status_code, response.text)
        return None


# def write_playlist_to_csv(playlist_id):
#     playlist = get_playlist(playlist_id)
#     if playlist is None:
#         return
    
#     # Define CSV file and headers
#     with open('spotify_tracks.csv', mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(['Track Name', 'Track ID', 'Audio Features', 'Audio Analysis'])

#         # Loop through tracks in the playlist
#         for item in playlist['tracks']['items']:
#             track = item['track']
#             track_name = track['name']
#             track_id = track['id']

#             # Get audio features and analysis for the track
#             audio_features = get_track_audio_features(track_id)
#             audio_analysis = get_track_audio_analysis(track_id)

#             # Write to CSV
#             writer.writerow([track_name, track_id, audio_features, audio_analysis])

# # Call the function to write data to CSV
# write_playlist_to_csv('5c27ZSdCgRmdeLgHvKpyhu')

def write_playlist_track_audio_features_to_csv(playlist_id):
    playlist = get_playlist(playlist_id)
    if playlist is None:
        return
    
    # Define CSV file and headers
    with open('spotify_playlist_tracks_audio_features.csv', mode='w', newline='', encoding='utf-8') as file:

        features = ('danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo')

        writer = csv.writer(file)
        writer.writerow(['Track Name', 'Track ID'] + [f.capitalize() for f in features])

        # Loop through tracks in the playlist
        for item in playlist['tracks']['items']:
            track = item['track']
            track_name = track['name']
            track_id = track['id']

            # Get audio features for the track
            audio_features = get_track_audio_features(track_id)

            # Write to CSV
            writer.writerow([track_name, track_id] + [audio_features[f] for f in features])

# Call the function to write data to CSV
write_playlist_track_audio_features_to_csv('5c27ZSdCgRmdeLgHvKpyhu')
