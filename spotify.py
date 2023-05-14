import time

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import vlc
import logging
import threading
import time
import random


class Spotify:
    def __init__(self):
        self.song_thread = None
        self.client_id = 'a575491a5a1140c2923dc1696a36bbfe'
        self.client_secret = '2c84e86e013b4f8baa148e2bc343170d'

        client_credentials_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.player = vlc.MediaPlayer()


    def get_genre_uris(self, genre):
        search_query = 'genre:"%s"' % genre
        try:
            results = self.sp.search(q=search_query, type='track', limit=20)
            song_uris = [track['uri'] for track in results['tracks']['items'] if track['preview_url']]
        except Exception as e:
            logging.error(f"Error searching for songs with query '{search_query}': {e}")
            song_uris = []

        return song_uris

    def play_song_thread_func(self, media):
        self.player.set_media(media)
        self.player.play()
        time.sleep(1)

        while self.player.is_playing():
            time.sleep(1)


    def play_song_using_uri(self, uri):
        try:
            song = self.sp.track(uri)
            artist = song['artists'][0]['name']
            title = song['name']

            print('Playing %s by %s' % (title, artist))
            url = song['preview_url']
            media = vlc.Media(url)
            self.song_thread = threading.Thread(target=self.play_song_thread_func, args=(media,))
            self.song_thread.start()
            return 0
        except Exception as e:
            logging.error(f"Error playing song {uri}: {e}")
            return 1

    def model_point_of_contact(self, expression):
        uris = self.get_genre_uris(expression)
        random.shuffle(uris)
        self.player.stop()
        playing_flag = False

        for uri in uris:
            ret_code = self.play_song_using_uri(uri)

            # song played successfully without any error
            if not ret_code:
                playing_flag = True
                break

        if not playing_flag:
            print('Could not find any song')
            return 'Could not find any song'

        return 'Music Playing'