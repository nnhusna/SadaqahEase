# your_app_name/urls.py

from django.urls import path
from . import views
#from .views import

urlpatterns = [
    path('', views.SadaqahEase, name='SadaqahEase'), 
    path('login/', views.login_page, name='login_page'),
    path('loginadmin/', views.login_view, name='login_admin'), 
    path('logindonor/', views.login_donor, name='login_donor'),
    path('signupdonor/', views.signup_donor, name='signup_donor'),
    path('donorpage/', views.donor_mainpage, name='donor_mainpage'),
    path('logout/', views.logout_view, name='logout'),
    path('donor/profile/', views.donor_profile, name='donorprofile'),
    path('donor/profile/edit/', views.donor_edit_profile, name='donor_edit_profile'),
    path('treasurerpage/', views.treasurer_mainpage, name='treasurer_mainpage'),
    path('treasurer/campaigns/', views.manage_campaigns, name='manage_campaigns'),
    path('treasurer/campaigns/add/', views.add_campaign, name='add_campaign'),
    path('donate/', views.donate_page, name='donate_page'),
    path('submit-donation/', views.submit_donation, name='submit_donation'),
    path('donor/history/', views.donor_history, name='donor_history'),
    path('donor/delete/<str:donation_id>/', views.delete_donation, name='delete_donation'),
    path('donor/clear-history/', views.clear_donation_history, name='clear_donation_history'),
    path('treasurer/record-donation/', views.record_donation_page, name='record_donation_page'),
    path('treasurer/submit-tabung-donation/', views.submit_tabung_donation, name='submit_tabung_donation'),
    path('tabung/delete/<str:donationid>/', views.delete_tabung_donation, name='delete_tabung_donation'),
    path('tabung/edit/<str:donationid>/', views.edit_tabung_donation, name='edit_tabung_donation'),
    path('edit-general-donation/<str:donationid>/', views.edit_general_donation, name='edit_general_donation'),
   path('delete_general_donation/<str:donationid>/', views.delete_general_donation, name='delete_general_donation'),
    path('edit-campaign-donation/<str:donationid>/', views.edit_campaign_donation, name='edit_campaign_donation'),
    path('delete-campaign-donation/<str:donationid>/', views.delete_campaign_donation, name='delete_campaign_donation'),
    path('donor-campaigns/', views.donor_campaigns, name='donor_campaigns'),
    path('donate-campaign/<str:campaign_id>/', views.donate_campaign, name='donate_campaign'),
    path('campaigns/edit/<str:campaignid>/', views.edit_campaign, name='edit_campaign'),
    path('campaigns/delete/<str:campaignid>/', views.delete_campaign, name='delete_campaign'),
    path('treasurer/financial/', views.financial_page, name='financial_page'),
    path('treasurer/financial/edit/<int:financialid>/', views.edit_financial, name='edit_financial'),
    path('treasurer/financial/delete/<int:financialid>/', views.delete_financial, name='delete_financial'),
    path('allocate-fund/', views.allocate_fund_page, name='allocate_fund_page'),
    path('allocate-fund/edit/<int:allocateid>/', views.edit_allocate_fund, name='edit_allocate_fund'),
    path('allocate-fund/delete/<int:allocateid>/', views.delete_allocate_fund, name='delete_allocate_fund'),
    path('admin-main/', views.admin_mainpage, name='admin_mainpage'),
     path('manage-donors/', views.manage_donors, name='manage_donors'),
    path('edit-donor/<str:donorid>/', views.edit_donor, name='edit_donor'),
    path('delete-donor/<str:donorid>/', views.delete_donor, name='delete_donor'),
     path('manage-treasurers/', views.manage_treasurers, name='manage_treasurers'),
    path('edit-treasurer/<str:treasurerid>/', views.edit_treasurer, name='edit_treasurer'),
    path('delete-treasurer/<str:treasurerid>/', views.delete_treasurer, name='delete_treasurer'),
    path('admin-campaigns/', views.manage_campaigns_admin, name='admin_manage_campaigns'),
    path('admin-campaigns/approve/<str:campaignid>/', views.approve_campaign, name='approve_campaign'),
    path('admin-campaigns/reject/<str:campaignid>/', views.reject_campaign, name='reject_campaign'),
    path('reportdonation/', views.report_donation_view, name='report_donation_view'),
    path('generate-report/', views.generate_report_pdf, name='generate_report_pdf'),
    path('donor/forgot-password/', views.forgot_password_donor, name='forgot_password_donor'),



]