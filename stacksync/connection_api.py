import json
import requests
from requests_oauthlib import OAuth1
import os
from stacksync.file_metadata import FileMetadata
from django.conf import settings
from base64 import *


class Api:
    def metadata(self, access_token_key, access_token_secret):
        url = settings.URL_STACKSYNC + '/folder/0'
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                     access_token_key, access_token_secret,
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
 
    def metadata_focus(self, folder_id, access_token_key, access_token_secret):
 
        url = settings.URL_STACKSYNC + '/folder/'+folder_id+'/contents'
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
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
 
    def upload_file(self, name, files, parent, access_token_key, access_token_secret ):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
     
        if parent == "":
            url = settings.URL_STACKSYNC + '/file?name='+name
        else:
            url = settings.URL_STACKSYNC + '/file?name='+name+'&parent='+parent
 
         
       
        r = requests.post(url,data=files, auth=headeroauth, headers=headers)
 
 
    def delete_file(self, file_id, access_token_key, access_token_secret):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
         
        url = settings.URL_STACKSYNC + '/file/'+file_id
        r = requests.delete(url, auth=headeroauth, headers=headers)
 
 
        flist = self.metadata(access_token_key, access_token_secret)
        return flist
    def delete_folder(self, folder_id, access_token_key, access_token_secret):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
        url = settings.URL_STACKSYNC + '/folder/'+folder_id
        r = requests.delete(url, auth=headeroauth, headers=headers)
 
        return r.json
        
    def rename_folder(self, folder_id, folder_name, access_token_key, access_token_secret):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
        url = settings.URL_STACKSYNC + '/folder/'+folder_id
        if not folder_name or folder_name == "":
            return json.dumps({'error':'nothing to update'})
        
        data = json.dumps({'name':folder_name})
        r = requests.put(url, data=data, auth=headeroauth, headers=headers)
        return r.content
    
    def rename_file(self, file_id, file_name, access_token_key, access_token_secret):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
        url = settings.URL_STACKSYNC + '/file/'+file_id
        if not file_name or file_name == "":
            return json.dumps({'error':'nothing to update'})
        
        data = json.dumps({'name':file_name})
        r = requests.put(url, data=data, auth=headeroauth, headers=headers)
        return r.content
    
    def download_file(self, file_id, access_token_key, access_token_secret):
         
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
         
        url = settings.URL_STACKSYNC + '/file/'+file_id+'/data'
 
        r = requests.get(url, auth=headeroauth, headers=headers, stream=False)
    
        return r.content
 
 
    def download_pdf(self, file_id, access_token_key, access_token_secret):
         
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
         
        url = settings.URL_STACKSYNC + '/file/'+file_id+'/data'
        
        r = requests.get(url, auth=headeroauth, headers=headers, stream=False)

        content_type = r.headers.get('content-type')
        pdf64 = b64encode(r.content)
        pdf = "data:"+content_type+";base64,"+pdf64
        return pdf
    def download_img(self, file_id, access_token_key, access_token_secret):
 
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
         
        url = settings.URL_STACKSYNC + '/file/'+file_id+'/data'
         
        r = requests.get(url, auth=headeroauth, headers=headers, stream=False)
        content_type = r.headers.get('content-type')
        image64 = b64encode(r.content)
        image = "data:"+content_type+";base64,"+image64
        return image
 
 
    def metadata_file(self, file_id, access_token_key, access_token_secret):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
                 signature_type='auth_header', signature_method='PLAINTEXT')
         
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
 
 
    def create_folder(self, folder_name, parent, access_token_key, access_token_secret):
        headers = {'Stacksync-api': 'v2'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                 access_token_key, access_token_secret,
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
