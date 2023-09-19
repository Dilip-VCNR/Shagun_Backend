"""Shagun_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import to include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path

from Shagun_backend.views import *

urlpatterns = [
    path('<str:slug>/', custom_404, name='catch-all'),
    path('api/app_compatibility', app_compatibility, name='app_compatibility'),
    path('api/check_user', check_user, name='check_user'),
    path('api/user_register', user_register, name='user_register'),
    path('api/get_user_profile', get_user_profile, name='get_user_profile'),
    path('api/edit_user', edit_user, name='edit_user'),
    path('api/add_transaction_history', add_transaction_history, name='add_transaction_history'),
    path('api/user_home_page', user_home_page, name='user_home_page'),
    path('api/gift_sent_list', gift_sent_list, name='gift_sent_list'),
    path('api/gift_sent_search', gift_sent_search, name='gift_sent_search'),
    path('api/gift_received_list', gift_received_list, name='gift_received_list'),
    path('api/gift_received_search', gift_received_search, name='gift_received_search'),
    path('api/gift_received_for_event', gift_received_for_event, name='gift_received_for_event'),
    path('api/get_greeting_cards', get_greeting_cards, name='get_greeting_cards'),
    path('api/track_transaction', track_transaction, name='track_transaction'),
    path('api/get_single_event', get_single_event, name='get_single_event'),
    path('api/get_my_event_list', get_my_event_list, name='get_my_event_list'),
    path('api/request_callback', request_callback, name='request_callback'),
    path('api/get_users_by_name_or_phone', get_users_by_name_or_phone, name='get_users_by_name_or_phone'),
    path('api/search_user_event', search_user_event, name='search_user_event'),
    path('api/get_my_all_invited_events', get_my_all_invited_events, name='get_my_all_invited_events'),
    path('api/get_my_notifications', get_my_notifications, name='get_my_notifications'),

    path('', admin_dashboard, name='admin_dashboard'),
    path('sign_up', sign_up, name='sign_up'),
    path('printer_login', printer_login, name='printer_login'),
    path('logout', logout, name='logout'),
    path('manage_event', manage_event, name='manage_event'),
    path('kyc_request', kyc_request, name='kyc_request'),
    path('event_request', event_request, name='event_request'),
    path('search_kyc_request', search_kyc_request, name='search_kyc_request'),
    path('search_event_request', search_event_request, name='search_event_request'),
    path('whatsapp_invite/eventId=<str:e_id>/', whatsapp_invite, name='whatsapp_invite'),
    path('search_event', dashboard_search_event, name='dashboard_search_event'),
    path('search_kyc', dashboard_search_kyc, name='dashboard_search_kyc'),
    path('search_bank', dashboard_search_bank, name='dashboard_search_bank'),
    path('search_user', dashboard_search_user, name='dashboard_search_user'),
    path('search_greetings', dashboard_search_greetings, name='dashboard_search_greetings'),
    path('search_printers', dashboard_search_printers, name='dashboard_search_printers'),
    path('search_delivery_vendors', dashboard_search_delivery_vendors, name='dashboard_search_delivery_vendors'),
    path('search_employee', dashboard_search_employee, name='dashboard_search_employee'),
    path('search_event_settlement', dashboard_search_event_settlement,
         name='dashboard_search_event_settlement'),
    path('add_events', add_events, name='add_events'),
    path('manage_event_types', manage_event_types, name='manage_event_types'),
    path('manage_location', manage_location, name='manage_location'),
    path('manage_kyc', manage_kyc, name='manage_kyc'),
    path('manage_bank_details', manage_bank_details, name='manage_bank_details'),
    path('manage_greeting_cards', manage_greeting_cards, name='manage_greeting_cards'),
    path('printer_manage_greeting_cards', printer_manage_greeting_cards, name='printer_manage_greeting_cards'),
    path('manage_users', manage_users, name='manage_users'),
    path('manage_employee', manage_employee, name='manage_employee'),
    path('manage_admin', manage_admin, name='manage_admin'),
    path('filter_kyc/status=<str:status>/', filter_kyc, name='filter_kyc'),
    path('filter_bank/status=<str:status>/', filter_bank, name='filter_bank'),
    path('filter_user/status=<str:status>/', filter_user, name='filter_user'),
    path('filter_kyc_request/status=<str:status>/', filter_kyc_request, name='filter_kyc_request'),
    path('filter_event_request/status=<str:status>/', filter_event_request, name='filter_event_request'),
    path('filter_transaction_lists/eventId=<int:event_id>/status=<int:status>/', filter_transaction_lists,
         name='filter_transaction_lists'),
    path('all_printer_jobs', all_printer_jobs, name='all_printer_jobs'),
    path('new_printer_jobs', new_printer_jobs, name='new_printer_jobs'),
    path('closed_printer_jobs', closed_printer_jobs, name='closed_printer_jobs'),
    path('Open_printer_jobs', Open_printer_jobs, name='Open_printer_jobs'),
    path('search_all_printer_jobs', search_all_printer_jobs, name='search_all_printer_jobs'),
    path('search_new_printer_jobs', search_new_printer_jobs, name='search_new_printer_jobs'),
    path('search_open_printer_jobs', search_open_printer_jobs, name='search_open_printer_jobs'),
    path('search_closed_printer_jobs', search_closed_printer_jobs, name='search_closed_printer_jobs'),
    path('add_employee', add_employee, name='add_employee'),
    path('add_admin', add_admin, name='add_admin'),
    path('edit_employee', edit_employee, name='edit_employee'),
    path('edit_admin', edit_admin, name='edit_admin'),
    path('enable_disable_employee', enable_disable_employee, name='enable_disable_employee'),
    path('get_employee_by_id', get_employee_by_id, name='get_employee_by_id'),
    path('manage_printers', manage_printers, name='manage_printers'),
    path('manage_delivery_vendors', manage_delivery_vendors, name='manage_delivery_vendors'),
    path('manage_settlement', manage_settlement, name='manage_settlement'),
    path('active_event_settlement', active_event_settlement, name='active_event_settlement'),
    path('add_events_type', add_events_type, name='add_events_type'),
    path('add_kyc', add_kyc, name='add_kyc'),
    path('add_bank', add_bank, name='add_bank'),
    path('add_greeting_cards', add_greeting_cards, name='add_greeting_cards'),
    path('printer_add_greeting_cards', printer_add_greeting_cards, name='printer_add_greeting_cards'),
    path('get_printer_by_id', get_printer_by_id, name='get_printer_by_id'),
    path('search_printers_status/status=<str:status>/', dashboard_search_printers_status,
         name='dashboard_search_printers_status'),
    path('search_delivery_vendors_status/status=<str:status>/', dashboard_search_delivery_vendors_status,
         name='dashboard_search_delivery_vendors_status'),
    path('search_greetings_status/status=<str:status>/', dashboard_search_greetings_status,
         name='dashboard_search_greetings_status'),
    path('search_employee_status/status=<str:status>/role=<str:role>/', dashboard_search_employee_status,
         name='dashboard_search_employee_status'),
    path('filtered_events_on_approval_status/status=<str:status>/', filtered_events_on_approval_status,
         name='filtered_events_on_approval_status'),
    path('transactions_settlement/eventId=<int:event_id>/', transactions_settlement, name='transactions_settlement'),
    path('search_transactions_settlement/eventId=<int:event_id>/', search_transactions_settlement, name='search_transactions_settlement'),
    path('filter_all_printer_jobs/status=<int:status>/', filter_all_printer_jobs, name='filter_all_printer_jobs'),
    path('filter_open_printer_jobs/status=<int:status>/', filter_open_printer_jobs, name='filter_open_printer_jobs'),
    path('printer_filter_all_jobs/status=<int:status>/', printer_filter_all_jobs, name='printer_filter_all_jobs'),
    path('printer_filter_open_jobs/status=<int:status>/', printer_filter_open_jobs, name='printer_filter_open_jobs'),

    path('printer_home_page', printer_home_page, name='printer_home_page'),
    path('printer_all_jobs', printer_all_jobs, name='printer_all_jobs'),
    path('printer_open_jobs', printer_open_jobs, name='printer_open_jobs'),
    path('printer_closed_jobs', printer_closed_jobs, name='printer_closed_jobs'),
    path('printer_new_jobs', printer_new_jobs, name='printer_new_jobs'),
    path('printer_search_all_jobs', printer_search_all_jobs, name='printer_search_all_jobs'),
    path('printer_search_greetings', printer_search_greetings, name='printer_search_greetings'),
    path('printer_search_open_jobs', printer_search_open_jobs, name='printer_search_open_jobs'),
    path('printer_search_closed_jobs', printer_search_closed_jobs, name='printer_search_closed_jobs'),
    path('printer_search_new_jobs', printer_search_new_jobs, name='printer_search_new_jobs'),
    path('printer_filter_greetings_cards/status=<int:status>/', printer_filter_greetings_cards, name='printer_filter_greetings_cards'),

    path('activate_deactivate_location/<int:location_id>/<int:status>/', activate_deactivate_location,
         name='activate_deactivate_location'),
    path('activate_deactivate_bank/<int:bank_id>/<int:status>/', activate_deactivate_bank,
         name='activate_deactivate_bank'),
    path('activate_deactivate_users/<int:user_id>/<int:status>/', activate_deactivate_users,
         name='activate_deactivate_users'),
    path('activate_deactivate_employee/<int:user_id>/<int:status>/<int:role>/', activate_deactivate_employee,
         name='activate_deactivate_employee'),
    path('activate_deactivate_printers/printerId=<int:printer_id>/status=<int:status>/', activate_deactivate_printers,
         name='activate_deactivate_printers'),
    path('activate_deactivate_delivery_vendors/printerId=<int:printer_id>/status=<int:status>/', activate_deactivate_delivery_vendors,
         name='activate_deactivate_delivery_vendors'),
    path('activate_deactivate_event_type/<int:event_type_id>/<int:status>/', activate_deactivate_event_type,
         name='activate_deactivate_event_type'),
    path('activate_deactivate_greeting_cards/<int:card_id>/<int:status>/', activate_deactivate_greeting_cards,
         name='activate_deactivate_greeting_cards'),
    path('printer_activate_deactivate_greeting_cards/cardId=<int:card_id>/status=<int:status>/', printer_activate_deactivate_greeting_cards,
         name='printer_activate_deactivate_greeting_cards'),
    path('activate_deactivate_kyc/<int:kyc_id>/<int:status>/', activate_deactivate_kyc, name='activate_deactivate_kyc'),
    path('activate_deactivate_event/<int:event_id>/<int:status>/', activate_deactivate_event,
         name='activate_deactivate_event'),
    path('set_event_status/<int:event_id>/<int:status>/', set_event_status, name='set_event_status'),
    path('set_KYC_request_status/requestId=<int:req_id>/completedBy=<str:cmpltd_by>/status=<int:status>/', set_KYC_request_status,
         name='set_KYC_request_status'),
    path('set_event_request_status/requestId=<int:req_id>/completedBy=<str:cmpltd_by>/status=<int:status>/', set_event_request_status,
         name='set_event_request_status'),
    path('edit_event_type', edit_event_type, name='edit_event_type'),
    path('edit_location', edit_location, name='edit_location'),
    path('edit_kyc/kycId=<int:kyc_id>/', edit_kyc, name='edit_kyc'),
    path('edit_event/eventId=<int:event_id>/', edit_event, name='edit_event'),
    path('edit_bank/bankId=<int:bank_id>/', edit_bank, name='edit_bank'),
    path('edit_employee/employeeId=<int:user_id>/', edit_employee, name='edit_employee'),
    path('edit_admin/adminId=<int:user_id>/', edit_admin, name='edit_admin'),
    path('edit_printer/printerId=<int:printer_id>/', edit_printer, name='edit_printer'),
    path('edit_delivery_vendors/deliveryVendorId=<int:vid>/', edit_delivery_vendors, name='edit_delivery_vendors'),
    path('edit_event/eventId=<int:event_id>/', edit_event, name='edit_event'),
    path('edit_greeting_cards', edit_greeting_cards, name='edit_greeting_cards'),
    path('printer_edit_greeting_cards', printer_edit_greeting_cards, name='printer_edit_greeting_cards'),

    path('activate_deactivate_user', activate_deactivate_user, name='activate_deactivate_user'),
    path('add_user_kyc', add_user_kyc, name='add_user_kyc'),
    path('update_user_kyc', update_user_kyc, name='update_user_kyc'),
    path('enable_disable_kyc', enable_disable_kyc, name='enable_disable_kyc'),
    path('get_kyc_by_id', get_kyc_by_id, name='get_kyc_by_id'),
    path('add_bank_details', add_bank_details, name='add_bank_details'),
    path('edit_bank_details', edit_bank_details, name='edit_bank_details'),
    path('get_bank_by_id', get_bank_by_id, name='get_bank_by_id'),
    path('create_event', create_event, name='create_event'),
    path('enable_disable_event', enable_disable_event, name='enable_disable_event'),
    path('get_event_by_id', get_event_by_id, name='get_event_by_id'),
    path('get_settlement_for_event/<int:status>/', get_settlement_for_event, name='get_settlement_for_event'),
    path('gift_event', gift_event, name='gift_event'),
    path('enable_disable_events_type', enable_disable_events_type, name='enable_disable_events_type'),
    path('edit_events_type', edit_events_type, name='edit_events_type'),
    path('get_event_type_list', get_event_type_list, name='get_event_type_list'),
    path('get_events_type_by_id', get_events_type_by_id, name='get_events_type_by_id'),
    path('add_location', add_location, name='add_location'),
    path('enable_disable_location', enable_disable_location, name='enable_disable_location'),
    path('edit_location', edit_location, name='edit_location'),
    path('get_location_by_id', get_location_by_id, name='get_location_by_id'),
    path('add_printer', add_printer, name='add_printer'),
    path('add_delivery_vendor', add_delivery_vendor, name='add_delivery_vendor'),
    path('edit_delivery_vendors', edit_delivery_vendors, name='edit_delivery_vendors'),
    path('enable_disable_printer', enable_disable_printer, name='enable_disable_printer'),
    path('edit_printer', edit_printer, name='edit_printer'),
    path('get_greetings_by_id', get_greetings_by_id, name='get_greetings_by_id'),

    path('add_ev', add_ev, name='add_ev'),
    path('event_admin', event_admin, name='event_admin'),
    path('manage_vendor', manage_vendor, name='manage_vendor'),
    path('enable_disable_vendor', enable_disable_vendor, name='enable_disable_vendor'),
    path('add_bank_list', add_bank_list, name='add_bank_list'),
    path('activate_deactivate_bank_list', activate_deactivate_bank_list, name='activate_deactivate_bank_list'),
    path('change_printer_jobs_status/jobId=<int:pjid>/status=<int:status>/jobs=<str:from_page>', change_printer_jobs_status, name='change_printer_jobs_status'),

]
