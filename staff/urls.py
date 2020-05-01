from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.StaffTopView.as_view(), name='top'),
    path('login/', views.StaffLoginView.as_view(), name='login'),
    path('signup/', views.StaffSignupView.as_view(), name='signup'),
]