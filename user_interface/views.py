
from django.views.generic import TemplateView, ListView
from .models import MainFunction


class HomePage(ListView):
    template_name = "user_interface/home.html"
    extra_context = {'name': 'Andrey'}
    model = MainFunction


class PlateInspection(TemplateView):
    ...


class CanInspection(TemplateView):
    ...


class FlangeInspection(TemplateView):
    ...

