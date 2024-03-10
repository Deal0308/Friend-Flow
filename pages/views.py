from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'home/home.html'

class AboutPageView(TemplateView):
    template_name = 'home/about.html'



@csrf_exempt
def get_data(request, *args, **kwargs):
    data = {
        'name': 'John',
        'age': 23,
        'location': 'Nairobi',
        'comments': ['Great post!', 'Nice work!'],
        'likes': 10,
        'dislikes': 2
    }
    return JsonResponse(data)
