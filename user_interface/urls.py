from django.urls import path
from .views import HomePage, PlateInspection


urlpatterns = [
    path('home/', HomePage.as_view(), name='home'),
    path('plate_inspection/', PlateInspection.as_view(), name='plate_inspection'),
]