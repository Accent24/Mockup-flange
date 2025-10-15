from django.urls import path
from .views import *


urlpatterns = [
    path('api/sdk_test/', test_sdk, name='api_sdk_test'),
    path('fill_form/update/<int:pk>/', FillFormUpdate.as_view(), name='fill_form_update'),
    path('fill_form/<int:pk>/', FillFormCreate.as_view(), name='fill_form'),
    path('system_exit/', sys_exit, name='exit'),
    path('', start_sdk, name='start_sdk'),
    path('home/', HomePage.as_view(), name='home'),
    path('inspection/plate_inspection/<int:pk>/', plate_inspection, name='plate_inspection'),
]