from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse

def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('home_view'))
        
    return render(request, 'seguridad/index.html')

def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('contrasena')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('home_view'))
        else:
            messages.add_message(request, messages.ERROR, 'El usuario/contraseña inválidos o la cuenta está desactivada')
            return redirect('/')

        return HttpResponse(f'Usuario: {user} - Clave: {pawd}')
    else:
        return redirect('/')


def log_out(request):
    logout(request)
    return redirect('/')


