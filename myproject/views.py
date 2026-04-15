from django.shortcuts import render

def homepage(request):
    #return HttpResponse("Hello, Welcome to the homepage!")
    return render(request,'home.html')

def about_us(request):
    #return HttpResponse("This is my About Us page.")
    return render(request,'about.html')    