
from stacksyncapp.forms import ContactForm, ArchivoForm
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

import os
from django.core.servers.basehttp import FileWrapper
from django.utils.timezone import utc
from datetime import timedelta
import datetime
import time


connect = Connection_api()
breadcrumbs = Breadcrumbs()

@login_required(login_url='/log_in')
def contact(request): 
	if request.method == 'POST': 
		form = ContactForm(request.POST) 
		if form.is_valid(): 
			cd = form.cleaned_data 
			send_mail(cd['subject'], cd['message'], cd.get('email', 'noreply@example.com'), ['juanjoolinares@gmail.com'],) 
		return render_to_response('thanks.html', {'form': form}, context_instance=RequestContext(request)) 
	else: 
		form = ContactForm() 
		user = request.user.get_full_name()
		return render_to_response('contactform.html', {'user':user, 'form': form}, context_instance=RequestContext(request)) 


@login_required(login_url='/log_in')
def thanks(request): 
	user = request.user.get_full_name()
	return render_to_response('thanks.html', {'user':user, 'form': form}, context_instance=RequestContext(request)) 


def log_in(request):
	if request.method == 'POST':
        	form = AuthenticationForm(request.POST)
	
		if form.is_valid:
	    		username = request.POST['username']
	    		password = request.POST['password']
	    		user = authenticate(username = username, password = password) 
	   			
	    		if user is not None:
				login(request, user)
				request.session.set_expiry(user.get_expdate())
	        		return HttpResponseRedirect('/')
	    		else:
				notvalid = True
	        		return render_to_response('login.html',{'form':form, 'notvalid':notvalid }, context_instance=RequestContext(request))

	else:
        	form = AuthenticationForm()
    		return render_to_response('login.html',{'form':form}, context_instance=RequestContext(request))

@cache_control(no_cache=True, must_revalidate=True, no_store=True) 
@login_required(login_url='/log_in')
def index(request):
    if request.method=='POST':
	files = request.FILES['file']
	filename = files.name
	connect.UploadFile(filename, files, request.session['last_folder'], request.user.get_token_id())

	if request.session['last_folder'] == "":
		return HttpResponseRedirect('/')
    	else:    
    		return HttpResponseRedirect('/focus/'+request.session['last_folder'])
    else:
	
	    request.session['last_folder'] = ""

	    user = request.user.get_full_name()
	    files = connect.Metadata(request.user.get_token_id())
	
	    pathlist = breadcrumbs.delCrumb()	

	    return render_to_response('index.html', {'user':user,'files':files, 'file_id':request.session['last_folder'], 'pathlist':pathlist }, context_instance=RequestContext(request))

@cache_control(no_cache=True, must_revalidate=True, no_store=True) 
@login_required(login_url='/log_in')
def index_focus(request, file_id):
    user = request.user.get_full_name()
    request.session['last_folder'] = file_id

    files = connect.Metadata_focus(file_id, request.user.get_token_id())
    pathlist = breadcrumbs.addCrumb(files[0])
    files.pop(0)

    if request.method=='POST':
	files = request.FILES['files']
	filename = files.name
	connect.UploadFile(filename, files, request.session['last_folder'], request.user.get_token_id())

	if request.session['last_folder'] == "":
		return HttpResponseRedirect('/')
    	else:    
    		return HttpResponseRedirect('/focus/'+request.session['last_folder'])
    else:	

    	return render_to_response('index.html', {'user':user,'files':files, 'file_id':request.session['last_folder'], 'pathlist':pathlist}, context_instance=RequestContext(request))

@login_required(login_url='/log_in')
def delete_file(request,file_id):
    files = connect.Delete(file_id, request.user.get_token_id())
    if request.session['last_folder'] == "":
	return HttpResponseRedirect('/')
    else:    
    	return HttpResponseRedirect('/focus/'+request.session['last_folder'])

@login_required(login_url='/log_in')
def download_file(request,file_id):
    listData = connect.Metadata_file(file_id, request.user.get_token_id())
    mimetype = listData[0]
    file_name = listData[1]
    files = connect.DownloadFile(file_id, request.user.get_token_id())

    wrapper = FileWrapper(file(files))
    response = HttpResponse(wrapper, content_type= mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    response['Content-Length'] = os.path.getsize(files)
    return response

@login_required(login_url='/log_in')
def new_folder(request,folder_name):
    listData = connect.Create_folder(folder_name, request.session['last_folder'], request.user.get_token_id())
    if request.session['last_folder'] == "":
	return HttpResponseRedirect('/')
    else:    
    	return HttpResponseRedirect('/focus/'+request.session['last_folder'])

@login_required(login_url='/log_in')
def popup_move(request, file_id):
	base = True
	
	if file_id == "root":
		files = connect.Metadata(request.user.get_token_id())
		base = False
		request.session['popup_folder'] = []
		request.session['popup_folder'].append("root")
		request.session.modified = True

	elif file_id == "back":
		request.session['popup_folder'].pop()
		file_back = request.session['popup_folder'][-1]
		if file_back == "root":
			files = connect.Metadata(request.user.get_token_id())
			base = False
		else:
			files = connect.Metadata_focus(file_back, request.user.get_token_id())
		request.session.modified = True
		
	else:
		files = connect.Metadata_focus(file_id, request.user.get_token_id())
		request.session['popup_folder'].append(file_id)
		request.session.modified = True

	return render_to_response('popupmove.html',{'files':files, 'base':base}, context_instance=RequestContext(request))
   
@cache_control(no_cache=True, must_revalidate=True, no_store=True) 
def pdf(request, file_id):
     connect.DownloadPdf(file_id, request.user.get_token_id())
     browser = request.META['HTTP_USER_AGENT'].split("/")[-2]
     browser = browser.split(" ")[-1]
     if browser == "Firefox":
     	return render_to_response('pdf.html',{'file_id':file_id}, context_instance=RequestContext(request))
     else:
	return render_to_response('pdf.html', {'file_id':file_id}, context_instance=RequestContext(request))

def img(request, file_id):
     user = request.user.get_full_name()
     connect.DownloadImg(file_id, request.user.get_token_id())
     return render_to_response('img.html', {'user':user, 'file_id' :file_id}, context_instance=RequestContext(request))

@login_required(login_url='/log_in')
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/log_in')




