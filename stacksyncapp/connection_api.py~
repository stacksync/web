
import json
import requests
import os
from stacksyncapp.fileMetadata import FileMetadata
from django.conf import settings


class Connection_api:    

	def Metadata(self, token_id):	
		
		url = settings.URL_STACKSYNC+'/metadata'
		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}

		r = requests.get(url, headers=headers, verify=False)
		response = r.status_code
		
		folderlist = []
		filelist = []
		if response == 200:
			r.json()
			json_data = json.loads(r.content)
					
			for i in json_data['contents']:
				fileMetadata = FileMetadata(i['filename'],i['server_modified'],i['file_id'], i['is_folder'], i['path'], i['size'], i['mimetype'])
				if i['is_folder'] == True:
					folderlist.append(fileMetadata)	
				else:
					filelist.append(fileMetadata)

		folderlist = folderlist + filelist
		return folderlist

	def Metadata_focus(self, file_id, token_id):	
		
		url = settings.URL_STACKSYNC+'/metadata?file_id='+file_id+'&list=true'
		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}

		r = requests.get(url, headers=headers, verify=False)
		response = r.status_code
		
		folderlist = []
		filelist = []
		if response == 200:
			r.json()
			json_data = json.loads(r.content)
			
			fileMetadata = FileMetadata(json_data['filename'],json_data['server_modified'],json_data['file_id'], json_data['is_folder'], json_data['path'], json_data['size'],"folder")
			folderlist.append(fileMetadata)	

			for i in json_data['contents']:
				fileMetadata = FileMetadata(i['filename'],i['server_modified'],i['file_id'], i['is_folder'], i['path'], i['size'], i['mimetype'])
				if i['is_folder'] == True:
					folderlist.append(fileMetadata)	
				else:
					filelist.append(fileMetadata)
	
		folderlist = folderlist + filelist		
		return folderlist

	def UploadFile(self, name, files, parent ,token_id):	
		if parent == "":
			url = settings.URL_STACKSYNC+'/files?file_name='+name
		else:
			url = settings.URL_STACKSYNC+'/files?file_name='+name+'&parent='+parent

		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}

		r = requests.put(url, headers=headers, verify=False, data=files)


	def Delete(self, file_id, token_id):	

		url = settings.URL_STACKSYNC+'/files?file_id='+file_id
		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}

		r = requests.delete(url, headers=headers, verify=False)
		
		flist = self.Metadata(token_id)
		return flist 

	def DownloadFile(self, file_id, token_id):	

		url = settings.URL_STACKSYNC+'/files?file_id='+file_id
		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}
		
		local_filename = "temporaryfile"
		r = requests.get(url, headers=headers, verify=False, stream=True)
		with open(local_filename, 'wb') as f:
        		for chunk in r.iter_content(chunk_size=1024): 
            			if chunk: # filter out keep-alive new chunks
                			f.write(chunk)
                			f.flush()
		return local_filename


	def DownloadPdf(self, file_id, token_id):	

		url = settings.URL_STACKSYNC+'/files?file_id='+file_id
		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}
		
		path = 'static/images'
		local_filename = "temporaryfile.pdf"
		r = requests.get(url, headers=headers, verify=False, stream=True)
		with open(os.path.join(path, local_filename), 'wb') as f:
        		for chunk in r.iter_content(chunk_size=1024): 
            			if chunk: # filter out keep-alive new chunks
                			f.write(chunk)
                			f.flush()

	def DownloadImg(self, file_id, token_id):	

		url = settings.URL_STACKSYNC+'/files?file_id='+file_id
		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}
		
		path = 'static/images'
		local_filename = "temporaryfile"
		r = requests.get(url, headers=headers, verify=False, stream=True)
		with open(os.path.join(path, local_filename), 'wb') as f:
        		for chunk in r.iter_content(chunk_size=1024): 
            			if chunk: # filter out keep-alive new chunks
                			f.write(chunk)
                			f.flush()


	def Metadata_file(self, file_id, token_id):	
		
		url = settings.URL_STACKSYNC+'/metadata?file_id='+file_id+'&list=true'
		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}

		r = requests.get(url, headers=headers, verify=False)
		response = r.status_code
		
		flist = []
		if response == 200:
			r.json()
			json_data = json.loads(r.content)

			flist.append(json_data['mimetype'])
			flist.append(json_data['filename'])
				
		return flist


	def Create_folder(self, folder_name, parent, token_id):	
		if parent == "":
			url = settings.URL_STACKSYNC+'/files?folder_name='+folder_name
		else:
			url = settings.URL_STACKSYNC+'/files?folder_name='+folder_name+'&parent='+parent

		headers = {'Stacksync-api':'true', 'x-auth-token': token_id}

		r = requests.post(url, headers=headers, verify=False)

		response = r.status_code
		if response == 200:
			r.json()
			json_data = json.loads(r.content)
			

		return response

