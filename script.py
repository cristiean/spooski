import csv
import os
import requests
import time
import random

# Retrieve client_id and client_secret from environment variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TRACK_FEATURES = (
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
)


def get_access_token():
    # Define the token URL and the necessary data
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Make the POST request to get the access token
    response = requests.post(url, headers=headers, data=data)

    # Check if the request was successful and print the token
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        print("Failed to retrieve token:", response.status_code, response.text)
        return None


def make_spotify_request(url, headers, max_retries=5, initial_backoff=1):
    # NOTE: Temporary rate limiting strategy
    time.sleep(0.5)
    
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            # Spotify Web API does not return a Retry-After in Header
            # TODO: Implement a better rate limiting strategy
            # https://community.spotify.com/t5/Spotify-for-Developers/retry-after-header-not-accessible-in-web-app/td-p/5433144
            # https://stackoverflow.com/questions/70311642/persistent-spotify-429-errors-with-ridiculous-retry-after-suggestion-of-76-000
            if retry_after:
                sleep_time = int(retry_after)
            else:
                sleep_time = initial_backoff * (2**attempt) + random.uniform(0, 1)
            print(f"Rate limited. Retrying after {sleep_time} seconds.")
            time.sleep(sleep_time)
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    print("Max retries reached. Request failed.")
    return None


def get_user_playlists(user_id):
    print(f"Retrieving playlists for user: {user_id}")
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    playlists = []
    while url:
        data = make_spotify_request(url, headers)
        if data:
            playlists.extend(data["items"])
            url = data.get("next")
        else:
            print(f"Failed to retrieve {user_id}'s playlist information")
            return None

    return playlists


def get_playlist_details(playlist_id):
    print(f"Retrieving details for playlist: {playlist_id}")
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    return make_spotify_request(url, headers)


def get_playlist_tracks(playlist_id, playlist_name=None):
    print(f"Retrieving tracks for playlist: {playlist_name}")
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    tracks = []
    while url:
        data = make_spotify_request(url, headers)
        if data:
            tracks.extend(data["items"])
            url = data.get("next")
        else:
            if playlist_name:
                print(f"Failed to retrieve tracks for playlist: {playlist_name}")
            return None

    return tracks


def get_track_audio_features(track_id, track_name):
    print(f"Retrieving audio features for track: {track_name}")
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    return make_spotify_request(url, headers)


def get_track_audio_analysis(track_id):
    print(f"Retrieving audio analysis for track: {track_id}")
    url = f"https://api.spotify.com/v1/audio-analysis/{track_id}"
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    return make_spotify_request(url, headers)


def write_all_user_playlist_tracks_to_csv(user_id):
    print(f"Starting to process all playlists for user: {user_id}")
    playlists = get_user_playlists(user_id)
    if playlists is None:
        print(f"Failed to retrieve playlists for user: {user_id}")
        return

    output_file = f"spotify_user_{user_id}_all_tracks_audio_features.csv"
    print(f"Writing data to file: {output_file}")
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Playlist Name", "Track Name", "Track ID"]
            + [f.capitalize() for f in TRACK_FEATURES]
        )

        for playlist in playlists:
            playlist_name = playlist["name"]
            playlist_id = playlist["id"]
            print(f"Processing playlist: {playlist_name}")
            full_playlist = get_playlist_tracks(playlist_id, playlist_name)

            if full_playlist is None:
                print(f"Failed to retrieve playlist: {playlist_name}")
                continue

            for item in full_playlist:
                track = item["track"]
                track_name = track["name"]
                track_id = track["id"]

                print(f"Processing track: {track_name}")
                audio_features = get_track_audio_features(track_id, track_name)
                if audio_features:
                    writer.writerow(
                        [playlist_name, track_name, track_id]
                        + [audio_features[f] for f in features]
                    )
                else:
                    print(f"Failed to retrieve audio features for track: {track_name}")

    print(f"Finished processing all playlists for user: {user_id}")
    print(f"Data has been written to: {output_file}")


def write_all_playlists_tracks_to_csv(playlist_ids):
    print(f"Starting to process playlists")

    output_file = "spotify_playlists_all_tracks_audio_features.csv"
    print(f"Writing data to file: {output_file}")
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Playlist Name", "Track Name", "Track ID"]
            + [f.capitalize() for f in TRACK_FEATURES]
        )

        for playlist_id in playlist_ids:
            print(f"Processing playlist ID: {playlist_id}")
            playlist_details = get_playlist_details(playlist_id)

            if playlist_details is None:
                print(
                    f"Failed to retrieve playlist details for playlist ID: {playlist_id}"
                )
                continue
            else:
                playlist_name = playlist_details["name"]
                print(f"Processing playlist: {playlist_name}")
                playlist_tracks = get_playlist_tracks(playlist_id, playlist_name)

            for item in playlist_tracks:
                track = item["track"]
                track_name = track["name"]
                track_id = track["id"]

                print(f"Processing track: {track_name}")
                audio_features = get_track_audio_features(track_id, track_name)
                if audio_features:
                    writer.writerow(
                        [playlist_name, track_name, track_id]
                        + [audio_features[f] for f in TRACK_FEATURES]
                    )
                else:
                    print(f"Failed to retrieve audio features for track: {track_name}")

    print(f"Finished processing all playlists")
    print(f"Data has been written to: {output_file}")


################################################################################


# Call the function to write data to CSV for a specific user
# user_id = "cristiean"  # Replace with the desired user ID
# print(f"Starting script for user: {user_id}")
# write_all_user_playlist_tracks_to_csv(user_id)
# print("Script execution completed")

# Call the function to write data to CSV for a list of playlists
playlist_ids = [
    "37i9dQZF1DXbITWG1ZJKYt",  # Jazz Classics
    "37i9dQZF1DWVlYsZJXqdym",  # Happy Pop
    "37i9dQZF1DX9sQDbOMReFI",  # West Coast Classics
    "37i9dQZF1DX0AMssoUKCz7",  # Tropical House
    "37i9dQZF1EIfI1FMWgkzcP",  # Old School House Mix
    "7i8PotqqlAb88Bwybh7PAk",  # Jazz House
    "37i9dQZF1EIgbjUtLiWmHt",  # Rap Mix
    "37i9dQZF1DWWEJlAGA9gs0",  # Classical Essentials
    "37i9dQZF1DX9qNs32fujYe",  # Heavy Metal
]
print(f"Starting script for playlists: {', '.join(playlist_ids)}")
write_all_playlists_tracks_to_csv(playlist_ids)
print("Script execution completed")
