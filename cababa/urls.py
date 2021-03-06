"""cababa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.top_view, name='top_view'),
    path('user_agreement/', views.user_agreement_view, name='user_agreement_view'),
    path('cast_agreement/', views.cast_agreement_view, name='cast_agreement_view'),
    path('privacy_policy/', views.privacy_policy_view, name='privacy_policy_view'),
    path('cancel_policy/', views.cancel_policy_view, name='cancel_policy_view'),
    path('specified_commercial_transactions_act/', views.specified_commercial_transactions_act_view, name='specified_commercial_transactions_act_view'),
    path('system/', views.system_view, name='system_view'),
    path('admin/', admin.site.urls),
    path('pre_register/', include('pre_register.urls')),
    path('guest/', include('guest.urls')),
    path('hostess/', include('hostess.urls')),
    path('reservations/', include('reservations.urls')),
    path('staff/', include('staff.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)