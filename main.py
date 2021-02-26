from __future__ import unicode_literals
import os
import pprint
import pickle
import youtube_dl
import re
from youtube_dl.utils import DownloadError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = 'client_secrets.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


class PlaylistDownloader():

    def __init__(self, credentials):
        self.credentials = credentials
        self.playlists = None

    def download_single_item(self, id):
        video_link = 'http://youtube.com/watch?v={}'.format(id)
        ydl_options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            try:
                ydl.download([video_link])
            except DownloadError:
                pass

    def list_playlists(self):
        if not self.playlists:
            youtube = build(API_SERVICE_NAME, API_VERSION,
                            credentials=self.credentials)
            request = youtube.playlists().list(part='snippet', maxResults=25, mine=True)
            response = request.execute()
            playlists = [{'id': item['id'], 'title': item['snippet']['title']}
                         for item in response['items']]
            self.playlists = playlists
        # return [p['title'] for p in self.playlists]
        # pl = [{'title': p['title'], 'id': p['id']} for p in self.playlists]
        return self.playlists

    def list_playlist_items(self, id):
        page_token = ''
        playlist_videos = []
        while page_token != None:
            youtube = build(API_SERVICE_NAME, API_VERSION,
                            credentials=self.credentials)
            selected_playlist = youtube.playlistItems().list(part='snippet, contentDetails',
                                                             maxResults=50, playlistId=id, pageToken=page_token)
            playlist = selected_playlist.execute()
            page_token = playlist.get('nextPageToken', None)
            videos = [{'position': video['snippet']['position'],
                       'title': video['snippet']['title'],
                       'id': video['contentDetails']['videoId']} for video in playlist['items']]
            playlist_videos += videos
        return playlist_videos

    def download_all(self):
        if not self.playlists:
            self.list_playlists()
        all_videos = []
        for playlist in self.playlists:
            all_videos += self.list_playlist_items(playlist['id'])

        for video in all_videos:
            self.download_single_item(video['id'])


starting_dir = os.path.dirname(os.path.abspath(__file__))

config = {
    'download': ('d', 'dl', 'download'),
    'show': ('s', 'sh', 'show')
}


def main():
    credentials = None
    # check if credentials exist if not make and write to file
    if os.path.exists('token.pickle'):
        print('Getting credentials from file')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing token')
            credentials.refresh(Request())
        else:
            print('Getting new token')
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_console()
            with open('token.pickle', 'wb') as token:
                print("Saving credentials")
                pickle.dump(credentials, token)
    pldl = PlaylistDownloader(credentials)
    user_input = ''
    while user_input not in ['q', 'quit', 'exit']:
        print('Choose operation (h for help):')
        user_input = input('>> ')
        #user_input = user_input.lower()
        cmd = re.split('\s+', user_input)[0].lower()
        if cmd in ['ls']:
            for playlist in pldl.list_playlists():
                print(playlist['title'])
        elif cmd in ['d', 'download', 'dl']:
            match = re.match(r'(d|dl|download)\s+(.*)', user_input, flags=re.I)
            target_playlist = match.group(2)
            target_id = None
            for item in pldl.list_playlists():
                if item['title'] == target_playlist:
                    target_id = item['id']
                    break
            if target_id:
                print('hit')
            else:
                print('No such playlist!')
        elif cmd in ['s', 'sh', 'show']:
            match = re.match(r'(s|sh|show)\s+(.*)', user_input, flags=re.I)
            target_playlist = match.group(2)
            print(target_playlist)
            print(user_input)
            for playlist in pldl.list_playlists():
                playlistId = playlist['id']
                if target_playlist == playlist['title']:
                    selected_playlist = pldl.list_playlist_items(playlistId)
                    for video in selected_playlist:
                        position = video['position'] + 1
                        title = video['title']
                        # full_video = video['position'], video['title']
                        full_video = f'{position}, {title}'
                        print(full_video)
        else:
            print('Invalid command!')


if __name__ == '__main__':
    main()
