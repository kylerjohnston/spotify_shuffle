#!/usr/bin/env python3
# Note you will have to set environment variables for
# SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI
import argparse
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_playlist_tracks(sp, playlist_id):
    """
    Get all tracks in a playlist, even if the playlist has more than 100 tracks.

    Args:
        sp (spotipy.Spotify): An authenticated Spotipy client instance.
        playlist_id (str): The ID of the playlist.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing each track in the playlist.
    """
    results = sp.playlist_tracks(playlist_id, fields="items(track(id)),next")
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    # Get the unique tracks
    unique_tracks = []
    track_ids = set()
    for track in tracks:
        track_id = track["track"]["id"]
        if track_id not in track_ids:
            unique_tracks.append(track)
            track_ids.add(track_id)

    return unique_tracks


def remove_tracks(sp, playlist_id, tracks):
    """
    Remove all occurrences of a list of tracks from a playlist.

    Args:
        sp (spotipy.Spotify): An authenticated Spotipy client instance.
        playlist_id (str): The ID of the playlist.
        tracks (List[Dict[str, Any]]): A list of dictionaries representing each track to remove.
    """
    # Get the list of track IDs to remove
    track_ids = [track["track"]["id"] for track in tracks]

    # Remove all occurrences of each track from the playlist
    for track_id in track_ids:
        sp.user_playlist_remove_all_occurrences_of_tracks(sp,
                                                          playlist_id,
                                                          [track_id])


def shuffle_playlist(playlist_id, client_id, client_secret, redirect_uri):
    # Create a SpotifyOAuth object to authenticate with the Spotify API
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope="playlist-modify-public playlist-modify-private"))

    # Get the list of tracks in the playlist
    tracks = get_playlist_tracks(sp, playlist_id)

    for i in range(0, len(tracks), 100):
        sp.user_playlist_remove_all_occurrences_of_tracks(sp,
                                                          playlist_id,
                                                          [track["track"]["id"] for track in tracks[i:i+100]])

    # Shuffle the tracks randomly
    random.shuffle(tracks)

    # Add the shuffled tracks to the playlist in batches of 100
    for i in range(0, len(tracks), 100):
        sp.playlist_add_items(playlist_id, [track["track"]["id"] for track in tracks[i:i+100]])


def get_playlist_id(url):
    """
    Extracts the playlist ID from a Spotify playlist URL.

    Args:
        url (str): The URL of the Spotify playlist.

    Returns:
        str: The ID of the Spotify playlist.
    """
    # Split the URL by slashes
    parts = url.split("/")

    # Find the index of the "playlist" string
    try:
        index = parts.index("playlist")
    except ValueError:
        raise ValueError("Invalid Spotify playlist URL.")

    # Get the ID of the playlist
    return parts[index + 1].split("?")[0]


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Shuffle a Spotify playlist.")
    parser.add_argument("playlist_url", type=str, help="URL of Spotify playlist to shuffle.")
    args = parser.parse_args()

    # Get client ID, client secret, and redirect URI from environment variables
    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
    redirect_uri = os.environ["SPOTIFY_REDIRECT_URI"]

    # Shuffle the playlist
    playlist_id = get_playlist_id(args.playlist_url)
    shuffle_playlist(playlist_id, client_id, client_secret, redirect_uri)
