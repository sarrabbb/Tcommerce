from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [
    path("signup/buyer", views.signup, name="signupbuyer"),
    path("signupchoice", views.signupchoice, name="signupchoice"),
    path("signup/provider", views.signupProvider ,name="signupProvider"),
    

    path("signin", views.signin, name="signin"),
    path("profile/<int:id>/", views.profile, name="profile"),
    path("logout", views.logout, name="logout"),
    path("product/", include("products.urls")),
    url(r"^$", views.home, name="home"),
    url(
        r"^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.activate,
        name="activate",
    ),
    
    path("delete_account", views.delete_account, name="delete_account"),
    # provider profile
    path('providerProfile/<int:id>/',views.providerProfile,name='providerProfile'),


    # admin
    path('admin/', views.main,name='main'),
    path('provider/', views.main2,name='main2'),

    path("delete_account_admin/<int:id>", views.delete_account_admin, name="delete_account_admin"),
    path("providerList", views.providerList, name="providerList"),

    path("userProfile/<int:id>",views.userProfile,name="userProfile"),

   
]
