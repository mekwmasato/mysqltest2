from django.urls import path
from . import views

app_name = "myapp"
urlpatterns = [
    path('',views.Login,name='Login'),
    path("logout",views.Logout,name="Logout"),
    path('register',views.AccountRegistration.as_view(), name='register'),
    path("home",views.home,name="home"),
    path('docsbot',views.docs,name="docs"),
    path("delete_session",views.delete_session,name="delete_session"),
    path('chat_api/', views.chat_api, name='chat_api'),
    path('voice_output/', views.voice_output, name='voice_output'),
]