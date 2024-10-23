
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views 

router = DefaultRouter()
router.register ('donation-requests', views.DonationRequestViewset)
router.register ('donation-history', views.DonationHistoryViewSet, basename='donation-history')
router.register ('donation-accepted', views.DonationAcceptedViewSet, basename='donation-accepted')
router.register('users', views.UserViewSet, basename='user')
router.register('contactForm', views.ContactViewSet, basename='contactForm')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('login/', views.UserLoginApiView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('active/<uid64>/<token>/', views.activate, name = 'activate'),

    path('accept-request/<int:donation_request_id>/', views.accept, name = 'accept'),
    path('cancel-request/<int:donation_request_id>/', views.cancel, name = 'cancel'),
    path('complete-request/<int:donation_request_id>/', views.complete, name = 'complete'),
    
    path('blood-group/<str:blood_group>/', views.blood_group_filter, name = 'blood_group_filter'),

    path('donate_blood_users/<int:user_id>/', views.UserAccountDetailView.as_view(), name='user-account-detail'),
]


