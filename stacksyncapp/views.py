from stacksyncapp.forms import contact_form, file_form
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.mail import EmailMessage
from django.shortcuts import render

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from stacksyncapp.connection_api import Connection_api
from stacksyncapp.breadcrumbs import Breadcrumbs
from django.core.mail import send_mail
from django.conf import settings

import os
from django.core.servers.basehttp import FileWrapper
from django.utils.timezone import utc
from datetime import timedelta
import datetime
import time

from models import CustomUser, CustomUserManager
import json
import requests
import datetime
import urllib
from requests_oauthlib import OAuth1
from urlparse import parse_qs




connect = Connection_api()
breadcrumbs = Breadcrumbs()


@login_required(login_url='/log_in')
def contact(request):
    if request.method == 'POST':
        form = contact_form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(cd['subject'], cd['message'], cd.get('email', 'noreply@example.com'),
                      ['juanjoolinares@gmail.com'], )
        return render_to_response('thanks.html', {'form': form}, context_instance=RequestContext(request))
    else:
        form = contact_form()
        user = request.user.get_full_name()
        return render_to_response('contactform.html', {'user': user, 'form': form},
                                  context_instance=RequestContext(request))


@login_required(login_url='/log_in')
def thanks(request):
    user = request.user.get_full_name()
    return render_to_response('thanks.html', {'user': user, 'form': form}, context_instance=RequestContext(request))


def log_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)

        if form.is_valid:
            username = request.POST['username']
            password = request.POST['password']
            oauth = OAuth1(client_key="b3af4e669daf880fb16563e6f36051b105188d413", client_secret="c168e65c18d75b35d8999b534a3776cf", callback_uri='oob')
            headers = {"STACKSYNC_API":"v2"}
     
            r = requests.post(url=settings.STACKSYNC_REQUEST_TOKEN_ENDPOINT, auth=oauth, headers=headers)
            var = r.content
     
            credentials = parse_qs(r.content)
            resource_owner_key = credentials.get('oauth_token')[0]
            resource_owner_secret = credentials.get('oauth_token_secret')[0]
     
            authorize_url = settings.STACKSYNC_AUTHORIZE_ENDPOINT + '?oauth_token='
            authorize_url = authorize_url + resource_owner_key
            params = urllib.urlencode({'email': username, 'password': password, 'permission':'allow'})
            headers = {"Content-Type":"application/x-www-form-urlencoded", "STACKSYNC_API":"v2"}
            response = requests.post(authorize_url, data=params, headers=headers)
     
            if "application/x-www-form-urlencoded" == response.headers['Content-Type']:
                parameters = parse_qs(response.content)
                verifier = parameters.get('verifier')[0]
     
                oauth2 = OAuth1("b3af4e669daf880fb16563e6f36051b105188d413",
                       client_secret="c168e65c18d75b35d8999b534a3776cf",
                       resource_owner_key=resource_owner_key,
                       resource_owner_secret=resource_owner_secret,
                       verifier=verifier,
                       callback_uri='oob')
                r = requests.post(url=settings.STACKSYNC_ACCESS_TOKEN_ENDPOINT, auth=oauth2, headers=headers)
                r.content
                credentials = parse_qs(r.content)
                resource_owner_key = credentials.get('oauth_token')[0]
                resource_owner_secret = credentials.get('oauth_token_secret')[0]
                try:
                    user = CustomUser.objects.get(username=username)
                    user.set_access_token_key(resource_owner_key)  
                    user.set_access_token_secret(resource_owner_secret)  
                    user.save()
                except CustomUser.DoesNotExist:
                    user = CustomUser(username=username, password=password, access_token_secret=resource_owner_secret, access_token_key=resource_owner_key)
                    user.save()
                user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                request.session.set_expiry(0)
                return HttpResponseRedirect('/')
        
        notvalid = True
        return render_to_response('login.html', {'form': form, 'notvalid': notvalid},
                                  context_instance=RequestContext(request))

    else:
        form = AuthenticationForm()
        return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/log_in')
def index(request):
    if request.method == 'POST':
        files = request.FILES['file']
        filename = files.name
        connect.upload_file(filename, files, request.session['last_folder'], request.user)

        if request.session['last_folder'] == "":
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/focus/' + request.session['last_folder'])
    else:

        request.session['last_folder'] = ""

        user = request.user.get_full_name()
        files = connect.metadata(request.user)

        pathlist = breadcrumbs.del_crumb()

        return render_to_response('index.html',
                                  {'user': user, 'files': files, 'file_id': request.session['last_folder'],
                                   'pathlist': pathlist}, context_instance=RequestContext(request))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/log_in')
def index_focus(request, file_id):
    user = request.user.get_full_name()
    request.session['last_folder'] = file_id

    files = connect.metadata_focus(file_id, request.user)
    pathlist = breadcrumbs.add_crumb(files[0])
    files.pop(0)

    if request.method == 'POST':
        files = request.FILES['files']
        filename = files.name
        connect.upload_file(filename, files, request.session['last_folder'], request.user)

        if request.session['last_folder'] == "":
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/focus/' + request.session['last_folder'])
    else:

        return render_to_response('index.html',
                                  {'user': user, 'files': files, 'file_id': request.session['last_folder'],
                                   'pathlist': pathlist}, context_instance=RequestContext(request))


@login_required(login_url='/log_in')
def delete_file(request, file_id):
    files = connect.delete(file_id, request.user)
    if request.session['last_folder'] == "":
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/focus/' + request.session['last_folder'])


@login_required(login_url='/log_in')
def download_file(request, file_id):
    listData = connect.metadata_file(file_id, request.user)
    mimetype = listData[0]
    file_name = listData[1]
    files = connect.download_file(file_id, request.user)

    wrapper = FileWrapper(file(files))
    response = HttpResponse(wrapper, content_type=mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    response['Content-Length'] = os.path.getsize(files)
    return response


@login_required(login_url='/log_in')
def new_folder(request, folder_name):
    listData = connect.create_folder(folder_name, request.session['last_folder'], request.user)
    if request.session['last_folder'] == "":
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/focus/' + request.session['last_folder'])


@login_required(login_url='/log_in')
def popup_move(request, file_id):
    base = True

    if file_id == "root":
        files = connect.metadata(request.user)
        base = False
        request.session['popup_folder'] = []
        request.session['popup_folder'].append("root")
        request.session.modified = True

    elif file_id == "back":
        request.session['popup_folder'].pop()
        file_back = request.session['popup_folder'][-1]
        if file_back == "root":
            files = connect.metadata(request.user)
            base = False
        else:
            files = connect.metadata_focus(file_back, request.user)
        request.session.modified = True

    else:
        files = connect.metadata_focus(file_id, request.user)
        request.session['popup_folder'].append(file_id)
        request.session.modified = True

    return render_to_response('popupmove.html', {'files': files, 'base': base},
                              context_instance=RequestContext(request))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pdf(request, file_id):
    connect.download_pdf(file_id, request.user)
    browser = request.META['HTTP_USER_AGENT'].split("/")[-2]
    browser = browser.split(" ")[-1]
    if browser == "Firefox":
        return render_to_response('pdf.html', {'file_id': file_id}, context_instance=RequestContext(request))
    else:
        return render_to_response('pdf.html', {'file_id': file_id}, context_instance=RequestContext(request))


def img(request, file_id):
    user = request.user.get_full_name()
    connect.download_img(file_id, request.user)
    return render_to_response('img.html', {'user': user, 'file_id': file_id}, context_instance=RequestContext(request))


@login_required(login_url='/log_in')
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/log_in')




