from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login

User = get_user_model()
# Create your views here.
def login_view(request):
    if request.method == "POST":
        user = User.objects.get(username=request.POST['username'])
        if user.check_password(request.POST['password']) is True:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render(request, 'account/login.html')


def register_view(request):
    return render(request, 'account/register.html')