from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static

from .load import load_view

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('register/', views.register, name='register'),
    path('postcode/<int:postcode>/', views.postcode_home, name='postcode_home'),
    path('community/<int:id>/detail', views.group_detail, name='group_detail'),
    path('community/<int:id>/catalogue', views.group_catalogue, name='group_catalogue'),
    path('community/<int:id>/list', views.group_list, name='group_list'),
    path('community/<int:id>/members', views.group_members, name='group_members'),
    path('community/<int:id>/chat', views.group_chat, name='group_chat'),
    path('load/', load_view, name='load'),
    path('add/<int:price_id>/<int:group_id>/<int:order_id>', views.add_one, name='add_one'),
    path('minus/<int:price_id>/<int:group_id>/<int:order_id>', views.remove_one, name='remove_one')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
