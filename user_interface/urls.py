from django.urls import path
from .views import *


urlpatterns = [
    path('api/rough_alignment/', rough_alignment, name='rough_alignment'),
    path('api/automatic_alignment/', automatic_alignment, name='auto_alignment'),
    path('api/automatic_measurement/<int:num_dim>/', inspection, name='auto_inspection'),
    path('api/clear_measurement/', clear_measurement, name='clear_measurement'),
    path('api/close_camera_window/', ovc_close, name='close_ovc'),
    path('api/camera_window/', ovc, name='ovc'),
    path('api/spatial_scan/<str:collection>/<str:group>/', spatial_scan, name='spatial_scan'),
    path('api/measure/<str:collection>/<str:group>/<str:name>/<str:target_type>/', measure, name='measure_target'),
    path('api/template_and_connection/<str:template_name>/', load_and_start, name='load_and_start'),
    path('api/bring_foreground/', bring_window_foreground, name='bring_foreground'),
    path('api/instrument_test/', test_instrument, name='instrument_connection_test'),
    path('api/sdk_test/', test_sdk, name='api_sdk_test'),
    path('fill_form/update/<int:pk>/', FillFormUpdate.as_view(), name='fill_form_update'),
    path('fill_form/<int:pk>/', FillFormCreate.as_view(), name='fill_form'),
    path('system_exit/', sys_exit, name='exit'),
    path('', start_sdk, name='start_sdk'),
    path('home/', HomePage.as_view(), name='home'),
    path('inspection/plate_inspection/<int:pk>/', plate_inspection, name='plate_inspection'),
    path('inspection/flange_inspection/<int:pk>/', flange_inspection, name='flange_inspection'),
    path('test/', test, name='test'),
]