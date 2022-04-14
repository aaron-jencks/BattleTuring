from django.shortcuts import render

# Create your views here.


def playground(request):
    return render(request, 'playground.html', {})
