import json
import requests
from requests_oauthlib import OAuth1
import os
from stacksyncapp.fileMetadata import FileMetadata
from django.conf import settings


class Connection_api:
    def metadata(self, user):
        url = settings.URL_STACKSYNC + '/folder/0'
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                     user.get_access_token_key(), user.get_access_token_secret(),
                     signature_type='auth_header', signature_method='PLAINTEXT')
        r = requests.get(url, auth=headeroauth, headers=headers)
        response = r.status_code

        folder_list = []
        file_list = []
        if response == 200:
            r.json()
            json_data = json.loads(r.content)

            for item in json_data['contents']:
                file_metadata = FileMetadata(item['filename'], item['modified_at'], item['id'],
                                             item['is_folder'], item['size'], item['mimetype'])
                if item['is_folder']:
                    folder_list.append(file_metadata)
                else:
                    file_list.append(file_metadata)

        folder_list = folder_list + file_list
        return folder_list

    def metadata_focus(self, folder_id, user):

        url = settings.URL_STACKSYNC + '/folder/'+folder_id+'/contents'
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
        r = requests.get(url, auth=headeroauth, headers=headers)

        response = r.status_code

        folder_list = []
        file_list = []
        if response == 200:
            r.json()
            json_data = json.loads(r.content)

            fileMetadata = FileMetadata(json_data['filename'], json_data['modified_at'], json_data['id'],
                                        json_data['is_folder'], json_data['size'], json_data['mimetype'] )
            folder_list.append(fileMetadata)

            for item in json_data['contents']:
                fileMetadata = FileMetadata(item['filename'], item['modified_at'], item['id'],
                                            item['is_folder'], item['size'], item['mimetype'])
                if item['is_folder'] == True:
                    folder_list.append(fileMetadata)
                else:
                    file_list.append(fileMetadata)

        folder_list = folder_list + file_list
        return folder_list

    def upload_file(self, name, files, parent, user):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
    
        if parent == "":
            url = settings.URL_STACKSYNC + '/file?name='+name
        else:
            url = settings.URL_STACKSYNC + '/file?name='+name+'&parent='+parent

        
      
        r = requests.post(url,data=files, auth=headeroauth, headers=headers)


    def delete(self, file_id, user):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
        
        url = settings.URL_STACKSYNC + '/file/'+file_id
        r = requests.delete(url, auth=headeroauth, headers=headers)


        flist = self.metadata(user)
        return flist

    def download_file(self, file_id, user):
        
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
        
        url = settings.URL_STACKSYNC + '/file/'+file_id+'/data'


        local_filename = "temporaryfile"
        r = requests.get(url, auth=headeroauth, headers=headers, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename


    def download_pdf(self, file_id, user):
        
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
        
        url = settings.URL_STACKSYNC + '/file/'+file_id+'/data'
        r = requests.get(url, auth=headeroauth, headers=headers, stream=True)
   

        path = 'static/images'
        local_filename = "temporaryfile.pdf"
        r = requests.get(url, headers=headers, verify=False, stream=True)
        with open(os.path.join(path, local_filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()

    def download_img(self, file_id, user):

        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
        
        url = settings.URL_STACKSYNC + '/file/'+file_id+'/data'
        
        path = 'stacksync/static/images/'
        local_filename = 'temporaryfile'
        
        
        r = requests.get(url, auth=headeroauth, headers=headers, stream=True)
        with open(os.path.join(path+ local_filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            


    def metadata_file(self, file_id, user):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
        
        #TODO: Review the folder handle
        url = settings.URL_STACKSYNC + '/file/'+file_id

        r = requests.get(url, auth=headeroauth, headers=headers)

        response = r.status_code

        flist = []
        if response == 200:
            r.json()
            json_data = json.loads(r.content)

            flist.append(json_data['mimetype'])
            flist.append(json_data['filename'])

        return flist


    def create_folder(self, folder_name, parent, user):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 user.get_access_token_key(), user.get_access_token_secret(),
                 signature_type='auth_header', signature_method='PLAINTEXT')
        
        
        if parent == "":
            data = {'name':folder_name}
        else:
            data = {'name':folder_name, 'parent':parent}
        
        data = json.dumps(data)
        url = settings.URL_STACKSYNC + '/folder'
        r = requests.post(url,data=data, auth=headeroauth, headers=headers)

        response = r.status_code
        if response == 200:
            r.json()
            json_data = json.loads(r.content)

        return response

