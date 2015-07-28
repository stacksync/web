# -*- coding: utf-8 -*-
from urlparse import parse_qs
from urllib import urlencode, unquote
from datetime import datetime, timedelta
from base64 import b64decode

from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import ugettext as _
from requests_oauthlib import OAuth1

import requests
import psycopg2
import json
import easywebdav
from stacksync import keystone
from stacksync.connection_api import Api
from stacksync.bread_crumbs import BreadCrumbs
from stacksync.forms import contact_form

connect = Api()
breadcrumbs = BreadCrumbs()
path = []
global webdav
global owncloud_loaded
owncloud_loaded = False


#Funcion encargada del loggin del usuario
#Input:  -request, recibe los parametros generales de django
#Output: -se devuelve httpResponse cuando falla el acceso por usuario invalido o error de stacksync
#        -se devuelve HttpResponseRedirect cuando se conecta correctamente
#        -se devuelve render_to_response para redirigir a la pantalla de login si el usuario ha introducido mal alguno de los datos
def log_in(request):
    global owncloud_loaded
    owncloud_loaded = False
    try:
        if request.session['email']:
            return HttpResponseRedirect('/')
    except:
        None
    notvalid = False
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)

        if form.is_valid:
            username = request.POST['username']
            password = request.POST['password']
            oauth = OAuth1(client_key="b3af4e669daf880fb16563e6f36051b105188d413", client_secret="c168e65c18d75b35d8999b534a3776cf", callback_uri='oob')
            headers = {"STACKSYNC_API":"v2"}
            try:                
                con_up = psycopg2.connect(database = settings.MANAGER_DATABASE, user = settings.MANAGER_USER, host = settings.MANAGER_HOST, port=settings.MANAGER_PORT, password = settings.MANAGER_PASS)
                con_up.close()
                r = requests.post(url=settings.STACKSYNC_REQUEST_TOKEN_ENDPOINT, auth=oauth, headers=headers, verify=False)                
                if r.status_code != 200:
                    return render_to_response('error.html')
            except:
                return render_to_response('error.html')
            
            credentials = parse_qs(r.content)
            resource_owner_key = credentials.get('oauth_token')[0]
            resource_owner_secret = credentials.get('oauth_token_secret')[0]
     
            authorize_url = settings.STACKSYNC_AUTHORIZE_ENDPOINT + '?oauth_token='
            authorize_url = authorize_url + resource_owner_key
            params = urlencode({'email': username, 'password': password, 'permission':'allow'})
            headers = {"Content-Type":"application/x-www-form-urlencoded", "STACKSYNC_API":"v2"}
            try:
                response = requests.post(authorize_url, data=params, headers=headers, verify=False)                
            except:
                return render_to_response('error.html')
            
            if "application/x-www-form-urlencoded" == response.headers['Content-Type']:
                parameters = parse_qs(response.content)
                verifier = parameters.get('verifier')[0]
     
                oauth2 = OAuth1("b3af4e669daf880fb16563e6f36051b105188d413",
                       client_secret="c168e65c18d75b35d8999b534a3776cf",
                       resource_owner_key=resource_owner_key,
                       resource_owner_secret=resource_owner_secret,
                       verifier=verifier,
                       callback_uri='oob')
                try:
                    r = requests.post(url=settings.STACKSYNC_ACCESS_TOKEN_ENDPOINT, auth=oauth2, headers=headers, verify=False)
                except:
                    return render_to_response('error.html')
                credentials = parse_qs(r.content)
                resource_owner_key = credentials.get('oauth_token')[0]
                resource_owner_secret = credentials.get('oauth_token_secret')[0]
                initialize_session(request, resource_owner_key, resource_owner_secret, username)
                return HttpResponseRedirect('/')

            notvalid = True
            return render_to_response('login.html', {'form': form, 'notvalid': notvalid}, context_instance=RequestContext(request))
        
        notvalid = True
        return render_to_response('login.html', {'form': form, 'notvalid': notvalid}, context_instance=RequestContext(request))

    else:
        form = AuthenticationForm()
        return render_to_response('login.html', {'form': form, 'notvalid': notvalid}, context_instance=RequestContext(request))

#Funcion que carga la pagina del usuario en la que se visualizan las carpetas y ficheros del usuario
#Input:     -request, parametros generales de django
#           -file_id, id del directorio del que se muestra los datos, el caso por defecto es 0 que se trata del directorio general del usuario
#Output:    -HttpResponse, en caso de error con las llamadas a la API
#           -render_to_response, con la pagaina index.html y toda la informacion relativa a los datos del usuario como quotas, ficheros, etc 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request, file_id = '0'):                            
    try:           
        if request.session['email']:            
            try:
                files = connect.metadata(file_id, request.session['access_token_key'], request.session['access_token_secret'])
                shared = []                
                for fl in files:
                    if fl.is_folder:
                        fl.users = json.dumps(connect.get_members_of_folder(fl.file_id, request.session['access_token_key'], request.session['access_token_secret']))
                        if fl.users.count('email') > 1:
                            shared.append(fl.file_id)
            except:
                return HttpResponse(content="<h1>Internal Server Error</h1>", status=500)
            if file_id == '0':
                pathlist = breadcrumbs.del_crumb()
                request.session['last_folder'] = ''
            else:                
                request.session['last_folder'] = file_id                
                pathlist = breadcrumbs.add_crumb(files[0])     
                files.pop(0)
            quota_bar = 0
            if request.session['quota_assigned'] != 0:
                quota_used = float(connect.get_quota(request)['quota_used'])               
                quota_bar = float(quota_used)/float(request.session['quota_assigned'])*100.0   

            #return render_to_response('index.html', {'user': request.session['email'], 'files': files, 'file_id': request.session['last_folder'],
            #                                         'pathlist': pathlist,'quota_used_bar': round(quota_bar, 2), 'quota_used': round(quota_used, 2),
            #                                          'quota_assigned': request.session['quota_assigned'], 'shared': shared},context_instance=RequestContext(request))
            decryptError = request.session.get('decrypt_error', 0)
            request.session['decrypt_error'] = 0
            return render_to_response('index.html', {'user': request.session['email'], 'files': files, 'file_id': request.session['last_folder'],'quota_used_bar': round(quota_bar, 2),'quota_assigned': request.session['quota_assigned'],
                                                     'quota_used': round(quota_used, 2),'pathlist': pathlist, 'shared': shared, 'encrypt_option': request.session.get('encrypt_option', 0), 'encrypt_pass': request.session.get('encrypt_pass', ''), 'decrypt_error': decryptError},context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect('/log_in')
    except:
        return HttpResponseRedirect('/log_in')
    

#Funcion que elimina los ficheros o directorios
def delete(request, file_id):    
    try:        
        tmp = file_id.split(',')        
        if not tmp:
            return setMessageInfo(_("errorGeneric"), 400)
        if len(tmp) == 1:
            tmp[0] = file_id
        for file_id in tmp:           
            metadata = connect.metadata(file_id,request.session['access_token_key'], request.session['access_token_secret'])
            if metadata[0].is_folder:
                users = connect.get_members_of_folder(file_id,request.session['access_token_key'], request.session['access_token_secret'])
                for user in users:
                    if user['is_owner']:
                        owner = user['email']
                if request.session['email'] != owner:
                    return setMessageInfo(_("sharedwu"), 400)
                else:
                    connect.delete(file_id, True, request.session['access_token_key'], request.session['access_token_secret'])
            else:
                connect.delete(file_id, False, request.session['access_token_key'], request.session['access_token_secret'])
    except Exception as e:
        print(e)
        return setMessageInfo(_("errorGeneric"), 400)
    return setMessageInfo(_("successDelete"), 200)
 
#Descarga el fichero seleccionado
def download_file(request, file_id):
    try:
        listData = connect.metadata_file(file_id, request.session['access_token_key'], request.session['access_token_secret'])
        mimetype = listData[0]
        file_name = listData[1]
        previous_name = file_name
        if '_encrypted' in file_name:
            file_name = file_name.split('_encry')[0]
        files = connect.download_file(previous_name, file_id, request, mimetype, request.session['access_token_key'], request.session['access_token_secret'])
        if files == False:
            request.session['decrypt_error'] = 1
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            request.session['decrypt_error'] = 0
            response = HttpResponse(files, content_type=mimetype)
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            response['Content-Length'] = len(files)
    except Exception as e:
        print(e)
        return render_to_response('error.html')
    return response

#Crea una carpeta nueva en el espacio del usuario 
def new_folder(request, folder_name):    
    try:
        response = connect.create_folder(folder_name, request.session['last_folder'], request.session['access_token_key'], request.session['access_token_secret'])
        if response.status_code != 201:           
            if response.text.strip() == 'Folder already exists.':
                return setMessageInfo(_("nameRepeatFile") + ' [' + folder_name + ']', 400)
            else:
                return setMessageInfo(_("errorGeneric"), 400)
    except:
        return setMessageInfo(_("errorGeneric"), 400)
    return setMessageInfo(_("successNewFolder"), 200)
    
#Modifica el nombre del fichero o directorio
def rename(request, ids, name = '', parent_id = 'root'):
    connect.createURL(request,ids)
    try:
        name = unquote(b64decode(name))
        if parent_id == 'root':
            response = connect.rename(ids, name, parent_id, request.session['access_token_key'], request.session['access_token_secret'])
        else:
            response = connect.rename(ids, name, parent_id, request.session['access_token_key'], request.session['access_token_secret'])
        
        if response.status_code != 200:            
            return setMessageInfo(_("errorGeneric"), 400)           
    except:
        return setMessageInfo(_("errorGeneric"), 400)
    return setMessageInfo(_("successRename"), 200)    


def popup_move(request, file_id, file_name, parent_id):

    try:
        hist = request.session.get('path', ['root'])
        base = True
        if parent_id == "root":
            files = connect.metadata('0', request.session['access_token_key'], request.session['access_token_secret'])
            base = False
            hist = ['root']
        elif parent_id == "back":
            hist.pop()
            file_back = hist[-1]
            if file_back == '':
                file_back = 'root'
            if file_back == "root":
                files = connect.metadata('0', request.session['access_token_key'], request.session['access_token_secret'])
                base = False
            else:
                files = connect.metadata(file_back, request.session['access_token_key'], request.session['access_token_secret'])
        else:
            files = connect.metadata(parent_id, request.session['access_token_key'], request.session['access_token_secret'])
            if parent_id != hist[-1]:
                hist.append(parent_id)
        request.session['path'] = hist

        for file in (file for file in files if file.mimetype == 'inode/directory'):
            if file.file_id == int(file_id):
                files.remove(file)
        if len(files) == 0:
            return setMessageInfo(_("nofolders"), 400)
        else:
            return render_to_response('popupmove.html', {'files': files, 'base': base}, context_instance=RequestContext(request))
    except Exception as e:
        return setMessageInfo(_("errorGeneric"), 400)
 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pdf(request, file_id):
    try:
        pdf_metadata = connect.metadata_file(file_id, request.session['access_token_key'], request.session['access_token_secret'])
        pdf_content = connect.download_pdf(file_id, request.session['access_token_key'], request.session['access_token_secret'])
    except:
        return render_to_response('error.html')
    browser = request.META['HTTP_USER_AGENT'].split("/")[-2]
    browser = browser.split(" ")[-1]
   
    return render_to_response('pdf.html', {'file_id': file_id, 'pdf_content':pdf_content, 'file_name':pdf_metadata[1]}, context_instance=RequestContext(request))

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def img(request, file_id):
    user = request.session['email']
    try:
        image = connect.download_img(file_id, request.session['access_token_key'], request.session['access_token_secret'])
    except:
        return HttpResponse(content="<h1>Internal Server Error</h1>", status=500)
    return render(request,'img.html', {'user': user, 'file_id': file_id, 'img':image})

def log_out(request):    
    request.session.set_expiry(datetime.now() - timedelta(hours=24))
    for sesskey in request.session.keys():
        del request.session[sesskey]       
    return HttpResponseRedirect('/log_in')

def share_folder(request, folder_id):    
    try:
        unformatted_users = request.body.split(',')
        addresees = [user.strip() for user in unformatted_users]
        for addres in addresees:
            if addres == '':
                addresees.remove(addres)
        [validate_email(user) for user in addresees]
        dis = []
        usrs = connect.get_members_of_folder(folder_id,request.session['access_token_key'], request.session['access_token_secret'])
        for usr in usrs:
            dis.append(usr['email'])
            if usr['is_owner']:
                addresees.append(usr['email'])
        elim = []
        for d in dis:
            if d not in addresees:
                elim.append(d)
        if len(addresees) >= len(dis):
            addresees.append(request.session['email'])
            response = connect.share_folder(folder_id, addresees, request.session['access_token_key'], request.session['access_token_secret'])
            #Avisar por email cuando se comparte una carpeta
            for addres in addresees:
                if addres != request.session['email']:
                    send_mail('Carpeta compartida', 'El usuario '+request.session['email']+'ha compartido una carpeta con usted.',
                              'noreply@tissat.com', [addres], fail_silently=False)
            if response.status_code != 201:
                return setMessageInfo(_("errorGeneric"), 400)
        elif len(addresees) < len(dis):
            response = connect.unshare_folder(folder_id, elim, request.session['access_token_key'], request.session['access_token_secret'])
            if response.status_code != 201:
                return setMessageInfo(_("errorGeneric"), 400)
        else:
            return setMessageInfo(_("errorGeneric"), 400)
    except Exception as e:
        print(e)
        return setMessageInfo(_("errorGeneric"), 400)   
    return setMessageInfo(_("successShare"), 200)   

def get_members_of_folder(request, folder_id):
    try:
        json_response = connect.get_members_of_folder(folder_id, request.session['access_token_key'], request.session['access_token_secret'])
    except:
        return render_to_response('error.html')
    return HttpResponse(json.dumps(json_response))

def move_element(request, element_id, element_name, parent_id):
    try:
        if parent_id == 'root':
            request.session['last_folder'] = 'root'
        elif parent_id == 'back':
            parent_id = request.session['popup_folder'][-1]
            request.session['last_folder'] = parent_id
        else:
            request.session['last_folder'] = parent_id

        element_name = str(unquote(b64decode(element_name)))
        metadata = connect.metadata(element_id, request.session['access_token_key'], request.session['access_token_secret'])
        files = metadata[0]
        if parent_id != 'root':
            users = connect.get_members_of_folder(parent_id, request.session['access_token_key'], request.session['access_token_secret'])
        else:
            users = [{'is_owner': True, 'email': request.session['email']}]
            parent_id = '0'
        response = connect.move_element(element_id, element_name, parent_id, request.session['access_token_key'], request.session['access_token_secret'])
        if response.status_code != 200:
            return setMessageInfo(_("errorGeneric"), 400)
        if files.parent_id != None:
            users = connect.get_members_of_folder(files.parent_id,request.session['access_token_key'], request.session['access_token_secret'])
    except:
        return setMessageInfo(_("errorGeneric"), 400)
    return setMessageInfo(_("successMoved"), 200)

def upload_file(request):   
    try:         
        if len(request.FILES) < 1:
            return setMessageInfo('', 101)        
        for files in request.FILES:
            files = request.FILES[files]
            filename = files.name
            #users_with_capacity = 0            
            if request.session['last_folder'] != '':
                users = connect.get_members_of_folder(request.session['last_folder'],request.session['access_token_key'], request.session['access_token_secret'])
            else:
                users = [{'is_owner': True, 'email': request.session['email']}]            
            #for user in users:
            #    data = connect.get_quota(request,user['email'])
            #    quota = data['quota_used']
            #    limit = data['quota_limit']
            #    if limit > quota + files.size:
            #        users_with_capacity += 1
            #if True or users_with_capacity == len(users):                
            response = connect.upload_file(filename, request, files, request.session['last_folder'],request.session['access_token_key'], request.session['access_token_secret'])
            if response.status_code != 201:                             
                    #for user in users:           
                    #    if files.size == 0:
                    #        files.size = 1             
                #    connect.update_used_quota(request,user['email'],files.size)                     
                #else:                    
                if response.text.strip() == 'This name is already used in the same folder. Please use a different one.':
                    return setMessageInfo(_("nameRepeatFile") + ' [' + filename + ']', 400)
                else:        
                    return setMessageInfo(_("errorGeneric") + ' -' + response.text + '- [' + filename + ']', 400)
            #else: 
                #if users_with_capacity > 1:                   
                #    return setMessageInfo(_("storageUsersLimit"), 400)
                #else:                    
                    #return setMessageInfo(_("storageUserLimit"), 400)                   
    except Exception as e:
        print e
        return setMessageInfo(_("errorGeneric"), 400)    
    return setMessageInfo(_("successUpload"), 200)    

def initialize_session(request,resource_owner_key,resource_owner_secret,username):
    request.session['access_token_key'] = resource_owner_key
    request.session['access_token_secret'] = resource_owner_secret
    request.session['email'] = username
    data = connect.get_quota(request)
    request.session['quota_assigned'] = data['quota_limit']
    request.session['quota_used'] = data['quota_used']
    request.session.set_expiry(0)
    
#When the user want send a mail to the develop team, this function do the job
def contact(request):    
    if request.method == 'POST':
        form = contact_form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(cd['subject'], cd['message'], cd.get('email', 'noreply@example.com'),
                      ['desarrollotissat@gmail.com'])
        #return render_to_response('thanks.html', {'quota_used': round(request.session['quota_used'], 2), 'quota_assigned': request.session['quota_assigned']},
        #                          context_instance=RequestContext(request))
        return render_to_response('thanks.html', context_instance=RequestContext(request))
    else:
        form = contact_form()
        user = request.session['email']
        quota_used = float(connect.get_quota(request)['quota_used'])
        return render_to_response('contactform.html', {'user': user, 'form': form, 'quota_used': round(quota_used, 2), 'quota_assigned': request.session['quota_assigned'], 'encrypt_option': request.session.get('encrypt_option', 0), 'encrypt_pass': request.session.get('encrypt_pass', '')},context_instance=RequestContext(request))
        #return render_to_response('contactform.html', {'user': user, 'form': form}, context_instance=RequestContext(request))

#Load the page with the thanks
def thanks(request):
    user = request.session['email']
    form = contact_form()
    return render_to_response('thanks.html', {'user': user, 'form': form}, context_instance=RequestContext(request))

def forgotten(request):
    if request.method == 'POST':
        form = contact_form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            id = keystone.checkEmail(keystone.getTokenAdmin(),cd['email'])
            if id != 0:
                message = "Para restarurar su password de Stacksync acceda a la siguiente URL: " + settings.LOCAL_URL + "/restorepassword/" + cd['email'] + \
                          "\n\nTo restore your Stacksync password click in the next URL: " + settings.LOCAL_URL + "/restorepassword/" + cd['email']
                send_mail('Restore password of Stacksync', message, cd.get('email', 'noreply@example.com'),
                      [cd['email']])
                #return render_to_response('thanks.html', {'quota_used': 0, 'quota_assigned':0},
                #                  context_instance=RequestContext(request))
                return render_to_response('thanks.html', context_instance=RequestContext(request))
            else:
                return render_to_response('forgotten.html', {'incorrect':True}, context_instance=RequestContext(request))
    return render_to_response('forgotten.html', {}, context_instance=RequestContext(request))

def setMessageInfo(msg = '', codes = '', log= ''):
    message = {}
    message['message'] = msg
    message['code'] = codes
    return HttpResponse(json.dumps({'message': message['message'], 'code': message['code']}), status = codes, content_type='application/json')

def logFile(msg):
    d = datetime.now()
    name = "syslog-" + str(d.year)+ "-" + str(d.month)
    file = open(name,'a+')
    file.write(str(d.now()) + " " + msg + "\n")
    file.close()

def encriptacion(request):
    if request.POST.get('encrypt_option', 0) == 0:
        request.session['encrypt_option'] = 0
    else:
        request.session['encrypt_option'] = 1
    request.session['encrypt_pass'] = request.POST.get('encrypt_pass', '')

    request.session['last_pass'] = request.POST.get('last_pass', 0)

    file_id = request.POST.get('file_id', '')
    if file_id == '':
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect('/download/'+file_id)
    
def owncloud(request):
        user = request.POST.get('owncloud_user', '')
        password = request.POST.get('owncloud_pass', '')
        owncloud_dir = request.POST.get('owncloud_dir', '')
        global webdav
        webdav = easywebdav.connect(owncloud_dir , username=user, password = password, protocol='http', port=8080, verify_ssl=False)
        response = connect.create_folder('owncloud'+ '_'+ user , '0', request.session['access_token_key'], request.session['access_token_secret'])
        if response.content != 'Folder already exists.':
            json_dict = json.loads(response.content)
            parent = str(json_dict['id'])
        else:
            response = connect.metadata('0', request.session['access_token_key'], request.session['access_token_secret'])
            for attr in response:
                if attr.name == 'owncloud'+ '_'+ user:
                    parent = str(attr.file_id)
        for f in webdav.ls("/remote.php/webdav/"):
            if (f.name == '/remote.php/webdav/') == False:
                if(f.contenttype == ''):
                    create_folders_owncloud(request, f, parent)
                else:
                    fsock = open('prueba', "w", 0)
                    webdav.download(f.name, fsock)
                    fsock = open('prueba', "r", 0)
                    nameSplit = f.name.replace('/remote.php/webdav/', '').replace('%20', ' ').split('/')
                    name = nameSplit[len(nameSplit)-1]
                    response = connect.metadata(parent, request.session['access_token_key'], request.session['access_token_secret'])
                    upload = True
                    for attr in response:
                        if attr.name == name:
                            upload = False
                        if upload:       
                            connect.upload_file(name, request, fsock, parent ,request.session['access_token_key'], request.session['access_token_secret'])
        global owncloud_loaded
        owncloud_loaded = True
        return HttpResponseRedirect('/')



def create_folders_owncloud(request, f, parent):
    try:
        seen = []
        seen = set(seen)
        name_folder_split = str(f.name.replace('/remote.php/webdav/', '')).split('/')
        name = name_folder_split[len(name_folder_split)-2]
        seen.add(name)
        response = connect.create_folder(name , parent, request.session['access_token_key'], request.session['access_token_secret'])
        if response.content != 'Folder already exists.':
            json_dict = json.loads(response.content)
            parent = str(json_dict['id'])
        else:
            response = connect.metadata(parent, request.session['access_token_key'], request.session['access_token_secret'])
            for attr in response:
                if attr.name == name:
                    parent = str(attr.file_id)
        for fi in webdav.ls(f.name):
            name_folder_split = str(fi.name.replace('/remote.php/webdav/', '')).split('/')
            name = name_folder_split[len(name_folder_split)-2]
            if name not in seen and fi.contenttype == '': #subfolder
                create_folders_owncloud(request, fi, parent)
            else: #file found
                fsock = open('prueba', "w", 0)
                webdav.download(fi.name, fsock)
                fsock = open('prueba', "r", 0)
                nameSplit = fi.name.replace('/remote.php/webdav/', '').replace('%20', ' ').split('/')
                name = nameSplit[len(nameSplit)-1]
                response = connect.metadata(parent, request.session['access_token_key'], request.session['access_token_secret'])
                upload = True
                for attr in response:
                    if attr.name == name:
                        upload = False
                if upload:       
                    connect.upload_file(name, request, fsock, parent ,request.session['access_token_key'], request.session['access_token_secret'])
            #print response.id
        return setMessageInfo(_("successNewFolder"), 200)
    except Exception as e:
        print(e)
        return setMessageInfo(_("errorGeneric"), 400)
        
   
    

@csrf_exempt
def pathlist(request):
    data = request.POST.get('path')
    request.session['path'] = json.loads(data)
    return HttpResponse(request.session.get('path'))