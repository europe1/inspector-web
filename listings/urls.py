from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.listing_create, name='listing_create'),
    path('<int:listing_id>/', views.listing, name='listing'),
    path('<int:listing_id>/delete/', views.listing_delete, name='listing_delete'),
    path('<int:listing_id>/edit/', views.listing_create, name='listing_edit'),
    path('<int:listing_id>/bump/', views.listing_bump, name='listing_bump'),
    path('newseller/', views.seller_add, name='seller_add'),
    path('seller/<seller_username>/', views.seller, name='seller_profile'),
    path('review/<int:review_id>/', views.review_edit, name='review_edit'),
    path('login/',
    auth_views.LoginView.as_view(template_name='listings/login.htm',
        redirect_authenticated_user=True), name='login'),
    path('register/', views.user_register, name='user_register'),
    path('', include('django.contrib.auth.urls'))
]
