from django.shortcuts import render


def top_view(request):
    return render(request, 'cababa/index.html')

def system_view(request):
    return render(request, 'cababa/system.html')