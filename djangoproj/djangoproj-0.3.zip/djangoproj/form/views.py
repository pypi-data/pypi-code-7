from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from .forms  import ContactView
from django.contrib import messages


def contact(request):
    form = ContactView(request.POST or None)
    if form.is_valid():
        our_form = form.save(commit=False)
        our_form.save()
        messages.add_message(request, messages.INFO, 'Pesan anda sudah terkirim. Trims  :)')
        return HttpResponseRedirect('/')
    t = loader.get_template('contact.html')
    c = RequestContext(request, {'form': form,})
    return HttpResponse(t.render(c))