from django.conf import settings
from django.conf.urls.static import static

from django.urls import path,include
from .views import *
from django import views

urlpatterns = [
    path('',home_view,name="home"),
    path('about',about_view,name="about"),
    path('services',services_view,name="services"),
    path('services-details/<int:id>',service_detail_view,name="services_details"),

    path('teams',teams_view,name="teams"),
    path('contact',contact_view,name="contact"),
    path('faq',faq_view,name="faq"),
    path('enquiry',enquiry_view,name="enquiry"),
    path('gallery',Gallery_view,name="gallery"),
    path('gallery_detail/<int:id>',Gallery_detail_view,name="gallery_detail"),
    path('accounts/signup',signup_view,name="signup"),
    path('checkout/<int:id>',Checkout,name="checkout"),
    path('checkout_session/<int:id>/',checkout_session,name="checkout_session"),
    path('payment_success',payment_success,name="payment_success"),
    path('payment_cancel',payment_cancel,name="payment_cancel"),
    path('user-dashboard',user_dashboard_view,name="user-dashboard"),
    path('user-profile',user_profile_view,name="user-profile"),
    path('user-change-password',user_change_password_view,name="user-change-password"),
    path('notification',notification_view,name="notification"),
    path('fetch_notification',fetch_notification_view,name="fetch_notification"),
    path('mark_read',mark_read_view,name="mark_read"),
    
    path('trainer-dashboard',trainer_dashboard_view,name='trainer-dashboard'),
    path('trainer-profile',trainer_profile_view,name="trainer-profile"),
    path('trainer-subscribers',Subscribers_view,name="trainer-subscribers"),
    path('trainer-payments',Payments_view,name="trainer-payments"),
    path('trainer-change-password',trainer_change_password_view,name="trainer-change-password"),
    path('trainer_notification',trainer_notification_view,name="trainer_notification"),
















]