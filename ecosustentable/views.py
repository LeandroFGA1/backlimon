from django.http import HttpResponse
from django.shortcuts import render
def home(request):
    return HttpResponse("Bienvenido a la página principal")
def index(request):
    return render(request, 'index.html')