from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('register/', views.register, name='register'),
    path('postcode/<int:postcode>/', views.postcode_home, name='postcode_home'),
    path('community/<int:id>/detail', views.group_detail, name='group_detail')
]