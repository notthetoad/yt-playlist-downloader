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
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_console()
            with open('token.pickle', 'wb') as token:
                print("Saving credentials")
                pickle.dump(credentials, token)
    # get response from api call
    youtube =  build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    request = youtube.playlists().list(part='snippet', maxResults=25, mine=True)
    response = request.execute()
    # print out all playlist names on 1 page
    for item in response['items']:
        pprint.pprint(item['snippet']['title'])
    # select a playlist
    user_input = input('Select a playlist: ')
    for item in response['items']:
        if user_input == item['snippet']['title']:
            # check if dir for playlist exists if not create
            starting_dir = os.path.dirname(os.path.abspath(__file__))
            new_path = os.path.join(starting_dir, user_input)
            if os.path.exists(item['snippet']['title']):
                # os.path.join(current_dir, os.mkdir(item['snippet']['title']))
                os.chdir(new_path)
            else:
                # os.path.join(current_dir, playlist_dir)
                # prnit('dir does not exist')
                os.mkdir(user_input)
                os.chdir(new_path)
                # pass
            id = item['id']
            page_token = ''
            # page_token = None
            # download and convert all playlist items private or deleted video crash program
            while page_token != None:
                selected_playlist = youtube.playlistItems().list(part='snippet, contentDetails', playlistId=id, maxResults=50, pageToken=page_token)
                playlist = selected_playlist.execute()
                page_token = playlist.get('nextPageToken', None)
                for video in playlist['items']:
                    position = video['snippet']['position']
                    title = video['snippet']['title']
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

