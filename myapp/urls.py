from django.urls import path

from . import views


app_name = "myapp"
urlpatterns = [
    path('',views.Login,name='Login'),
    path("logout",views.Logout,name="Logout"),
    path('register',views.AccountRegistration.as_view(), name='register'),
    path("home",views.home,name="home"),
    path('docsbot',views.docs,name="docs")
]