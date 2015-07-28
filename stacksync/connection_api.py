#encoding = utf-8

import cStringIO
import json
import urllib
import psycopg2
import requests
from base64 import b64encode, b64decode
from stacksync.file_metadata import FileMetadataHelper
from requests_oauthlib import OAuth1
from Crypto.Cipher import AES
from django.core.files.base import ContentFile
from django.conf import settings

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE) 
unpad = lambda s : s[0:-ord(s[-1])]

#LA CLASE API QUE SE ENCARGA DE CONECTAR CON STACKSYNC
class Api:
    ROOT_FOLDER = u'0'
    DEFAULT_FILE_URL = settings.URL_STACKSYNC + '/file/'
    DEFAULT_FOLDER_URL = settings.URL_STACKSYNC + '/folder/'

    #OBTIENE LOS METADATOS DE LA CARPETA 
    def metadata(self, folder_id, access_token_key, access_token_secret):
        url = self.DEFAULT_FOLDER_URL + folder_id +'/contents'
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        r = requests.get(url, auth=headeroauth, headers=headers, verify=False)
 
        folder_list = []
        file_list = []
        json_data = None
        if r.status_code == 200:
            json_data = r.json()
            file_metadata_helper = FileMetadataHelper(json_data)

            if folder_id != self.ROOT_FOLDER:
                file_metadata_helper.add_initial_subfolder_metadata(folder_list)

            file_metadata_helper.filter_metadata_by_type(file_list, folder_list)

        folder_list = folder_list + file_list        
        return folder_list
 
    #SUBE UN FICHERO AL SERVIDOR POR MEDIO DE STACKSYNC
    def upload_file(self, name, request, files, parent, access_token_key, access_token_secret ):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        encrypted_files, encrypted = self.encrypt(files, request)
        name = urllib.quote_plus(name.encode('utf-8'))
        if encrypted:
            name += '_encrypted'
        if parent:
            url = settings.URL_STACKSYNC + '/file?name='+name+'&parent='+parent
        else:
            url = settings.URL_STACKSYNC + '/file?name='+name
        return requests.post(url, data=encrypted_files, auth=headeroauth, headers=headers, verify=False)

    #FORMA EL HEADER CON LOS DATOS RELATIVOS AL OAUTH Y LAS CABECERAS NECESARIAS
    def get_oauth_headers(self, access_token_key, access_token_secret):
        headers = {'Stacksync-api': 'v2', 'Content-Type': 'application/json'}
        headeroauth = OAuth1(settings.STACKSYNC_CONSUMER_KEY, settings.STACKSYNC_CONSUMER_SECRET,
                             access_token_key, access_token_secret,
                             signature_type='auth_header', signature_method='PLAINTEXT')
        return headeroauth, headers

    #BORRA UN FICHERO O UN DIRECTORIO 
    def delete(self, file_id, is_folder, access_token_key, access_token_secret):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        if is_folder:
            url = self.DEFAULT_FOLDER_URL+file_id
        else:
            url = self.DEFAULT_FILE_URL+file_id
        return requests.delete(url, auth=headeroauth, headers=headers, verify=False)
        
    #CAMBIA EL NOMBRE DE UN FICHERO O DE UN DIRECTORIO
    def rename(self, ids, name, parent_id, access_token_key, access_token_secret):        
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        response = self.metadata(ids, access_token_key, access_token_secret)
        if response[0].is_folder:
            url = self.DEFAULT_FOLDER_URL+ids
        else:
            url = self.DEFAULT_FILE_URL+ids
        data = json.dumps({'id' : ids, 'name':name, 'parent' : parent_id})
        return requests.put(url, data=data, auth=headeroauth, headers=headers, verify=False)   
    
    #DESCARGA UN FICHERO
    def download_file( self,file_name, file_id, request, mimetype, access_token_key, access_token_secret):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        url = self.DEFAULT_FILE_URL+file_id+'/data'
        r = requests.get(url, auth=headeroauth, headers=headers, stream=False, verify=False)
        decrypted_file = self.decrypt(file_name, r.content, request, mimetype)
        return decrypted_file

    #DESCARGA UN PDF
    def download_pdf(self, file_id, access_token_key, access_token_secret):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        url = self.DEFAULT_FILE_URL+file_id+'/data'
        r = requests.get(url, auth=headeroauth, headers=headers, stream=False, verify=False)
        content_type = r.headers.get('content-type')
        pdf64 = b64encode(r.content)
        pdf = "data:"+content_type+";base64,"+pdf64
        return pdf

    #DESCARGA UNA IMAGEN
    def download_img(self, file_id, access_token_key, access_token_secret):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        url = self.DEFAULT_FILE_URL+file_id+'/data'
        r = requests.get(url, auth=headeroauth, headers=headers, stream=False, verify=False)
        content_type = r.headers.get('content-type')
        image64 = b64encode(r.content)
        image = "data:"+content_type+";base64,"+image64
        return image
 
    #OBTIENE LOS DATOS DE UN FICHERO
    def metadata_file(self, file_id, access_token_key, access_token_secret):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
         
        url = self.DEFAULT_FILE_URL+file_id
        r = requests.get(url, auth=headeroauth, headers=headers, verify=False)
        response = r.status_code
 
        flist = []
        if response == 200:
            json_data = r.json()

            flist.append(json_data['mimetype'])
            flist.append(json_data['filename'])
 
        return flist

    #CREA UNA CARPETA 
    def create_folder(self, folder_name, parent, access_token_key, access_token_secret):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)

        if parent:
            data = {'name': folder_name, 'parent':parent}
        else:
            data = {'name': folder_name}
         
        data = json.dumps(data)
        url = settings.URL_STACKSYNC + '/folder'
        return requests.post(url,data=data, auth=headeroauth, headers=headers, verify=False)        

    #COMPARTE UNA CARPETA
    def share_folder(self, folder_id, allowed_user_emails=[], access_token_key=None, access_token_secret=None):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        url = self.DEFAULT_FOLDER_URL + str(folder_id) + '/share'
        json_payload = json.dumps(allowed_user_emails)
        return requests.post(url, json_payload, auth=headeroauth, headers=headers, verify=False)

    #DESCOMPARTE UNA CARPETA
    def unshare_folder(self, folder_id, allowed_user_emails=[], access_token_key=None, access_token_secret=None):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        url = self.DEFAULT_FOLDER_URL + str(folder_id) + '/unshare'
        json_payload = json.dumps(allowed_user_emails)
        return requests.post(url, json_payload, auth=headeroauth, headers=headers, verify=False)

    #OBTENER LOS MIENBROS QUE TIENEN ACCESO A LA CARPETA
    def get_members_of_folder(self, folder_id, access_token_key=None, access_token_secret=None):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        url = self.DEFAULT_FOLDER_URL + str(folder_id) + '/members'
        response = requests.get(url, auth=headeroauth, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            response.reason = response.reason + ". "+response.content
            response.raise_for_status()
   
    #CAMBIA UN ELEMENTO DE SITIO 
    def move_element(self, element_id, element_name, parent_id, access_token_key, access_token_secret):
        headeroauth, headers = self.get_oauth_headers(access_token_key, access_token_secret)
        url = self.DEFAULT_FILE_URL+element_id        
        data = json.dumps({'id': element_id, 'name': element_name, 'parent': parent_id})
        return requests.put(url, data=data, auth=headeroauth, headers=headers, verify=False)       
    
    #OBTIENE LA CUOTA DEL USUARIO
    def get_quota(self, request, mail = ''):
        if mail == '':
            mail = request.session['email']        
        data = {'quota_limit':'0','quota_used':'0'}
        try:
            con = psycopg2.connect(database = settings.MANAGER_DATABASE, user = settings.MANAGER_USER, host = settings.MANAGER_HOST, port=settings.MANAGER_PORT, password = settings.MANAGER_PASS)
            cur = con.cursor()
            cur.execute("SELECT quota_used_logical, quota_limit FROM user1 WHERE email = '" + mail + "'")
            rows = cur.fetchall()            
            for row in rows:
                #data['quota_used_logical'] = long(row[0])
                data['quota_used'] = long(row[0])
                data['quota_limit'] = long(row[1])
        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
        finally:
            if con:
                con.close()
        if data['quota_used'] < 0:
            data['quota_used'] = 0
        return data
    """
    def exceeded_quota(self, request):
        try:
            size = request.FILES['file'].size
        except:
            return False
        if (request.session['quota_used'] + size) > (request.session['quota_assigned']):
            return True
        return False

    def update_used_quota(self, request, mail = '', quota= ''):
        if mail == '':
            mail = request.session['email']
        if quota == '':
            quota = request.session['quota_used']                       
        success = True     
        try:               
            conn = psycopg2.connect(database = settings.MANAGER_DATABASE, user = settings.MANAGER_USER, host = settings.MANAGER_HOST, port=settings.MANAGER_PORT, password = settings.MANAGER_PASS)
            #conn.autocommit = False 
            c = conn.cursor()  
            c.execute("UPDATE user1 SET quota_used = i.quota_used + " + str(quota) + " FROM (SELECT quota_used FROM user1 WHERE email = '" + mail + "') i  WHERE email = '" + mail + "'")
            conn.commit()                
            success = True
        except:                
            success = False
            #conn.rollback()
        finally:
            if c:
                c.close()
        return success            
    """
    
    #OBTIENE EL TAMAnyO DE LA CARPETA
    def folder_size(self, request, folder_id):
        size = 0
        elements = self.metadata(folder_id,request.session['access_token_key'], request.session['access_token_secret'])
        for elem in elements:
            if elem.is_folder:
                if str(elem.file_id) != folder_id:
                    size += self.folder_size(request, str(elem.file_id))
            else:
                size += elem.size
        return size

    #CREA UNA URL DEL FICHERO PARA COMPARTIR CON USUARIOS NO AUTENTCADOS
    def createURL(self,request,file_id):
        url = ""
        meta = self.metadata_file(file_id,request.session['access_token_key'], request.session['access_token_secret'])
        try:
            url = meta[2]
        except:
            None
        return url


    

    #ENCRIPTA EL FICHERO
    def encrypt(self, files, request):
        try:            
            encrypt = request.session.get('encrypt_option', 0)
            if encrypt == 0:
                return files, False
            else:                
                """
                gpg = gnupg.GPG(gnupghome='/tmp')                
                encrypt_pass = request.session.get('encrypt_pass', '')
                encrypted_data = gpg.encrypt_file(files, None, symmetric='AES256', passphrase=encrypt_pass)
                if not encrypted_data.ok:
                    return False   
                output = cStringIO.StringIO()
                output.write(encrypted_data.data)  
                return output 
                """
                key = request.session.get('encrypt_pass', '')
                IV = '1111111111111111'
                mode = AES.MODE_CBC
                data = files.read()
                ciphertext = AES.new(key, mode, IV).encrypt(pad(data))
                b64_data = b64encode(ciphertext)
                output = cStringIO.StringIO()
                output.write(b64_data)  
                return output, True          
        except Exception as e:
            print(e)          
            return False

    #DESENCRIPTA FICHEROS
    def decrypt(self,file_name,  files, request, mimetype):
        try:            
            if '_encrypted' in file_name:
                if request.session.get('last_pass', 0) == '1':
                    return files
                else:
                    """
                    gpg = gnupg.GPG(gnupghome='/tmp')
                    decrypted_data = gpg.decrypt(files, passphrase = request.session['encrypt_pass'])
                    if not decrypted_data.ok:
                        return False
                    return ContentFile(decrypted_data)
                    """
                    key = request.session.get('encrypt_pass', '')
                    IV = '1111111111111111'
                    mode = AES.MODE_CBC
                    data = files
                    dec_data = b64decode(data)
                    ciphertext = AES.new(key, mode, IV).decrypt(dec_data)
                    text = unpad (ciphertext)
                    return ContentFile(text)
            else:
                return files
        except Exception as e:
            print(e)   
            return files
        
        
        
        
    