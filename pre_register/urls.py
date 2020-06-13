from django.urls import path

from . import views

app_name = 'pre_register'

urlpatterns = [
    path('', views.PreRegistrationView.as_view(), name='form'),
    path('done/', views.pre_registration_done_view, name='done'),
]