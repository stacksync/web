# -*- encoding: utf-8 -*-

import json
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from keystoneclient.v2_0 import client
import requests
from webclient import settings


#Controla que la nueva password coincida en ambos inputs y si es asi la cambia en keystone
def restorepassword(request, user):
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        notvalid = False
        if request.POST["pass1"] == request.POST["pass2"]:
            token = getTokenAdmin()
            user_id = checkEmail(token,user)
            url = settings.KEYSTONE_USR_URL + '/users/' + user_id + '/OS-KSADM/password'
            headers = {'X-Auth-Token': token, 'Content-type': 'application/json'}
            data = '{"user":{"password":"'+request.POST["pass1"]+'"}}'
            result = requests.put(url, data=data, headers=headers, verify=False)
            #return render_to_response('login.html', {'form': form, 'notvalid': notvalid}, context_instance=RequestContext(request))
            return HttpResponseRedirect('/')
        else:
            return render_to_response('restorepassword.html',{'difieren': True, 'name': user}, context_instance=RequestContext(request))
    else:
        return render_to_response('restorepassword.html',{'name': user}, context_instance=RequestContext(request))

#Obtiene el token de admin para poder gestionar las contrasenyas de los usuarios
def getTokenAdmin():
    url = settings.KEYSTONE_AUTH_URL + '/tokens'
    headers = {'Content-type': 'application/json'}
    data = '{"auth":{"passwordCredentials":{"username": "'+settings.KEYSTONE_ADMIN_USER+'", "password": "'+settings.KEYSTONE_ADMIN_PASSWORD+'"},"tenantName": "'+settings.KEYSTONE_TENANT+'"}}'
    try:
        result = requests.post(url, data=data, headers=headers, verify=False)
        result = json.loads(result.content)
        token = result['access']['token']['id']
        return token
    except:
        return None

#Obtiene la informacion de los usuarios del sistema
def listUsers(token):
    url = settings.KEYSTONE_USR_URL + '/users'
    headers = {'X-Auth-Token': token}
    try:
        result = requests.get(url, headers=headers, verify=False)
        result = json.loads(result.content)
        return result
    except:
        return None

#Comprueba que el email sea de un usuario valido
def checkEmail(token,email):
    users = listUsers(token)
    user_id = 0
    for elem in users['users']:
        try:
            if elem['email'] == email:
                user_id = elem['id']
        except:
            None
    return user_id
