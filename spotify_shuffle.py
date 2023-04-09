#!/usr/bin/env python3
# Note you will have to set environment variables for
# SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI
import argparse
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def shuffle_playlist(playlist_id, client_id, client_secret, redirect_uri):
    # Create a SpotifyOAuth object to authenticate with the Spotify API
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope="playlist-modify-public playlist-modify-private"))

    # Get the list of tracks in the playlist
    results = sp.playlist_tracks(playlist_id, fields="items(track(id))")
    tracks = results["items"]

    # Shuffle the tracks randomly
    random.shuffle(tracks)

    # Replace the playlist with the shuffled tracks
    sp.playlist_replace_items(playlist_id, [track["track"]["id"] for track in tracks])


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
