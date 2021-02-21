import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = 'client_secrets.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_console()
    youtube =  build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    request = youtube.playlists().list(part='snippet', maxResults=25, mine=True)
    response = request.execute()
    for item in response['items']:
    #     pprint.pprint(item['id'])
        pprint.pprint(item['snippet']['title'])
    # pprint.pprint(response)
    user_input = input('Select a playlist: ')
    for item in response['items']:
        if user_input == item['snippet']['title']:
            id = item['id']
            selected_playlist = youtube.playlistItems().list(part='snippet, contentDetails', playlistId=id, maxResults=50).execute()
            # pprint.pprint(selected_playlist)
            for item in selected_playlist['items']:
                position = item['snippet']['position']
                title = item['snippet']['title']
                link = 'youtu.be/' + item['contentDetails']['videoId']
                print(position, title, '\n', link)




if __name__ == '__main__':
    main()

