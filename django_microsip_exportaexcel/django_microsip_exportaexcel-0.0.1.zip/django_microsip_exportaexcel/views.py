#encoding:utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
# user autentication
from .models import *
import csv
from django.http import HttpResponse
from django.views.generic.list import ListView

@login_required( login_url = '/login/' )
def index( request, template_name = 'django_microsip_exportaexcel/index.html' ):
   
    return render_to_response( template_name, {}, context_instance = RequestContext( request ) )

    

