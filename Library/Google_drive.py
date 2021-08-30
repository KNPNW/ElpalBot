from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.discovery import build
import telebot
import io
import os
import sys
import shutil

workdir = os.getcwd()[:-7]

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = workdir + 'Data/elpalbot-bd2c87160429.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


def get_bilds_photo(folder_name, photos_id, user_id):
    folder_id = get_folder_id(folder_name)
    if folder_id == '0':
        return
    if os.path.isdir(workdir + '/Output/cache/{}'.format(user_id)):
        shutil.rmtree(workdir + '/Output/cache/{}'.format(user_id))
    os.mkdir(workdir + '/Output/cache/{}'.format(user_id))
    for id in photos_id:
        file_id = get_file_id(id+'.jpeg', "'"+folder_id+"'")
        if file_id != '0':
            download_file(file_id, id+'.jpeg', user_id)


def get_obj_photos(folder_name, conract_id, user_id):
    folder_id = get_folder_id(folder_name)
    folder_obj_id = get_file_id(str(conract_id), "'"+folder_id+"'")
    if folder_obj_id == 0:
        return '0'
    if os.path.isdir(workdir + '/Output/cache/{}'.format(user_id)):
        shutil.rmtree(workdir + '/Output/cache/{}'.format(user_id))
    os.mkdir(workdir + '/Output/cache/{}'.format(user_id))
    files_id = get_files_id("'"+folder_obj_id+"'")
    if files_id == '0':
        return '0'
    name = 0
    for file in files_id:
        download_file(file, str(name)+".jpeg", user_id)
        name += 1
    return '1'


def get_file_id(file_name, folder):
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name, mimeType)",
                                   q="{} in parents".format(folder)).execute()
    results = results['files']
    for i in results:
        if i.get('name').upper() == file_name.upper():
            id = i.get('id')
            return id
    return '0'


def get_files_id(folder):
    results = service.files().list(pageSize=10,
                                   fields="nextPageToken, files(id, name, mimeType)", q="{} in parents".format(folder)).execute()
    nextPageToken = results.get('nextPageToken')
    while nextPageToken:
        nextPage = service.files().list(pageSize=10,
                                        fields="nextPageToken, files(id, name, mimeType, parents)",
                                        pageToken=nextPageToken, q="{} in parents".format(folder)).execute()
        nextPageToken = nextPage.get('nextPageToken')
        results['files'] = results['files'] + nextPage['files']

    results = results['files']
    if len(results) == 0:
        return '0'
    files_id = []
    for file in results:
        files_id.append(file['id'])
    return files_id


def get_folder_id(file_name):
    results = service.files().list(pageSize=10,
                                   fields="nextPageToken, files(id, name, mimeType)").execute()
    nextPageToken = results.get('nextPageToken')
    while nextPageToken:
        nextPage = service.files().list(pageSize=10,
                                        fields="nextPageToken, files(id, name, mimeType, parents)",
                                        pageToken=nextPageToken).execute()
        nextPageToken = nextPage.get('nextPageToken')
        results['files'] = results['files'] + nextPage['files']

    results = results['files']
    for i in results:
        if i.get('name').upper() == file_name.upper():
            id = i.get('id')
            return id
    return '0'



def download_file(file_id, name, user_id):
    request = service.files().get_media(fileId=file_id)
    filename = workdir + '/Output/cache/{}/{}'.format(user_id, name)
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()


def add_feedback(contract_id, user_id, name_folder):
    folder_id = get_folder_id(name_folder)
    chek_file_id = get_file_id(contract_id, "'"+folder_id+"'")
    if chek_file_id != '0':
        service.files().delete(fileId=chek_file_id).execute()

    file = workdir+'/Output/cache/{}/{}.txt'.format(user_id, contract_id)
    upload_text(folder_id, contract_id, file)


def upload_text(folder_id, name, file_path):
    file_metadata = {
        'name': name,
        'mimeType': 'text/plain',
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='text/plain', resumable=True)
    r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()




