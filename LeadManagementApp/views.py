from django.shortcuts import render,redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponseRedirect,Http404,JsonResponse
from django.contrib.auth import login, authenticate,logout
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION 
from django.contrib.contenttypes.models import ContentType

import csv,json

from .forms import LoginForm,AccountSettingsForm,UserForm
from .models import User
from LeadManagementProject.utils import (get_db_handle,get_leads_columns,processCsvFile,get_filters_from_request,
                                        get_leads_data,redirect_if_authenticated,get_filters)

db_handle,db_client = get_db_handle()

@user_passes_test(redirect_if_authenticated, login_url='/')
def login_request(request):
	if request.method == "POST":
		form = LoginForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return HttpResponseRedirect('/')
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = LoginForm()
	return render(request=request, template_name="registration/login.html", context={"form":form})

@login_required
def logout_request(request):
    logout(request)
    return HttpResponseRedirect('/login')

@login_required
def profile(request):
    if request.method == "POST":
        obj = User.objects.get(pk=request.user.id)
        form = AccountSettingsForm(request.POST or None, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.set_password(form.cleaned_data['password'])
            obj.save()
            LogEntry.objects.log_action(user_id=request.user.id,content_type_id=ContentType.objects.get_for_model(User).pk,
                        object_id=request.user.id,
                        object_repr=request.user.username,
                        action_flag=CHANGE,
                        change_message= request.user.username + " updated his profile")
            return JsonResponse({"error":0,"message":"updated successfully"})
        else:
            return JsonResponse({"error":1,"message":"the password must not be empty and must be equal to the confirmation password, the email also must be a valid one!"})

    else:
        form = AccountSettingsForm()
        data = User.objects.get(id=request.user.id)
        return render(request=request, template_name="registration/profile.html", context={"data":data,"form":form})

@login_required
def dashboard(request):
    if request.method == 'POST':
        leads = get_leads_data(0,10,get_filters_from_request(request))
        return JsonResponse({"data":leads},safe=False)
    if request.method == 'GET':
        leads = get_leads_data(0,10,{})
        return render(request, 'dashboard.html',{"leads":leads,"columns":get_leads_columns(),"filters":get_filters()})

@login_required
def users(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            users = User.objects.all()
            context = {'users':users}
            return render(request, 'users.html',context)
        else:
            print("ok")
    else:
        raise Http404("")

@login_required
def upload(request):
    if request.user.is_staff:
        if request.method == "POST":
            try:
                csv_file = request.FILES['csv_file']
            except Exception as e:
                return JsonResponse({'error':1,'message':'Please check that you have selected a csv file and that it is not damaged!'})
            else:
                try:
                    reader = csv.reader(line.decode('utf-8') for line in csv_file)
                    return JsonResponse(processCsvFile(reader))
                except Exception as e:
                    print(e)
                    return JsonResponse({'error':1,'message':'Error server side, please check well that the file is not damaged and try again!'})
        else:
            context = {}
            return render(request, 'upload.html',context)
    else:
        raise Http404("")

@login_required
def logs(request):
    if request.user.is_superuser:
        logs = LogEntry.objects.all().select_related('content_type','user')
        return render(request, 'logs.html',{"logs":logs})


