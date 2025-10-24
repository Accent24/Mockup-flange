from django.urls import path
from .views import *


urlpatterns = [
    path('api/measure/<str:collection>/<str:group>/<str:name>/<str:target_type>/', measure, name='measure_target'),
    path('api/template_and_connection/<str:template_name>/', load_and_start, name='load_and_start'),
    path('api/sdk_test/', test_sdk, name='api_sdk_test'),
    path('fill_form/update/<int:pk>/', FillFormUpdate.as_view(), name='fill_form_update'),
    path('fill_form/<int:pk>/', FillFormCreate.as_view(), name='fill_form'),
    path('system_exit/', sys_exit, name='exit'),
    path('', start_sdk, name='start_sdk'),
    path('home/', HomePage.as_view(), name='home'),
    path('inspection/plate_inspection/<int:pk>/', plate_inspection, name='plate_inspection'),
    path('inspection/flange_inspection/<int:pk>/', flange_inspection, name='flange_inspection'),
    ]