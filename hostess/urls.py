from django.urls import path

from . import views

app_name = 'hostess'

urlpatterns = [
    path('login/', views.HostessLoginView.as_view(), name='login'),
    path('callback/', views.HostessLoginCallbackView.as_view(), name='login_callback'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signup/done/', views.SignUpDoneView.as_view(), name='signup_done'),
    path('bot/webhook/', views.LineBotWebhookView.as_view(), name='bot_webhook'),
    path('invite/groups/<str:group_id>/', views.HostessGroupInviteView.as_view(), name='invite_group'),
    path('invite/<str:group_id>/', views.HostessInviteView.as_view(), name='invite'),
]