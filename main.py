from __future__ import unicode_literals
import os
import pprint
import pickle
import youtube_dl
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = 'client_secrets.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def main():
    credentials = None

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
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_console()
            with open('token.pickle', 'wb') as token:
                print("Saving credentials")
                pickle.dump(credentials, token)
    youtube =  build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    request = youtube.playlists().list(part='snippet', maxResults=25, mine=True)
    response = request.execute()
    for item in response['items']:
        pprint.pprint(item['snippet']['title'])
    user_input = input('Select a playlist: ')
    for item in response['items']:
        if user_input == item['snippet']['title']:
            id = item['id']
            page_token = ''
            while page_token != None:
                selected_playlist = youtube.playlistItems().list(part='snippet, contentDetails', playlistId=id, maxResults=50, pageToken=page_token)
                playlist = selected_playlist.execute()
                page_token = playlist.get('nextPageToken', None)
                for video in playlist['items']:
                    position = video['snippet']['position']
                    title = video['snippet']['title']
                    # link = 'youtu.be/{}'.format(video['contentDetails']['videoId'])
                    link = 'http://www.youtube.com/watch?v={}'.format(video['contentDetails']['videoId'])
                    print(position, title, '\n', link)
                    ydl_options = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192'
                        }]
                    }
                    with youtube_dl.YoutubeDL(ydl_options) as ydl:
                        ydl.download([link])

# Make directory for each playlist and download to them

if __name__ == '__main__':
    main()

