from django.urls import path
from . import views

app_name = 'documentation'

urlpatterns = [
    # ====================================
    # PUBLIC DOCUMENTATION ROUTES
    # ====================================

    # Homepage
    path('', views.doc_home, name='doc_home'),

    # Documentation articles
    path('docs/<slug:slug>/', views.doc_detail, name='doc_detail'),
    path('category/<slug:category_slug>/', views.category_docs, name='category_docs'),

    # FAQ section
    path('faq/', views.faq_list, name='faq_list'),
    path('faq/<slug:category_slug>/', views.faq_by_category, name='faq_by_category'),

    # Help center
    path('help/', views.help_center, name='help_center'),
    path('help/<int:help_id>/', views.help_detail, name='help_detail'),

    # Search functionality
    path('search/', views.doc_search, name='doc_search'),

    # App versions
    path('versions/', views.version_list, name='version_list'),
    path('versions/<str:version_number>/', views.version_detail, name='version_detail'),

    # Analytics (helpful buttons)
    path('ajax/mark-helpful/', views.mark_helpful, name='mark_helpful'),


    # ====================================
    # ADMIN MANAGEMENT ROUTES
    # ====================================

    # Dashboard
    path('admin/dashboard/', views.doc_admin_dashboard, name='admin_dashboard'),

    # Documentation management
    path('admin/docs/', views.manage_docs, name='manage_docs'),
    path('admin/docs/create/', views.create_doc, name='create_doc'),
    path('admin/docs/<int:doc_id>/edit/', views.edit_doc, name='edit_doc'),
    path('admin/docs/<int:doc_id>/delete/', views.delete_doc, name='delete_doc'),
    path('admin/docs/<int:doc_id>/publish/', views.publish_doc, name='publish_doc'),

    # Category management
    path('admin/categories/', views.manage_categories, name='manage_categories'),
    path('admin/categories/create/', views.create_category, name='create_category'),
    path('admin/categories/<int:cat_id>/edit/', views.edit_category, name='edit_category'),
    path('admin/categories/<int:cat_id>/delete/', views.delete_category, name='delete_category'),

    # FAQ management
    path('admin/faqs/', views.manage_faqs, name='manage_faqs'),
    path('admin/faqs/create/', views.create_faq, name='create_faq'),
    path('admin/faqs/<int:faq_id>/edit/', views.edit_faq, name='edit_faq'),
    path('admin/faqs/<int:faq_id>/delete/', views.delete_faq, name='delete_faq'),

    # Daily issue help management
    path('admin/help-issues/', views.manage_help_issues, name='manage_help_issues'),
    path('admin/help-issues/create/', views.create_help_issue, name='create_help_issue'),
    path('admin/help-issues/<int:help_id>/edit/', views.edit_help_issue, name='edit_help_issue'),
    path('admin/help-issues/<int:help_id>/delete/', views.delete_help_issue, name='delete_help_issue'),

    # Version management
    path('admin/versions/', views.manage_versions, name='manage_versions'),
    path('admin/versions/create/', views.create_version, name='create_version'),
    path('admin/versions/<int:version_id>/edit/', views.edit_version, name='edit_version'),
    path('admin/versions/<int:version_id>/delete/', views.delete_version, name='delete_version'),
    path('admin/versions/<int:version_id>/set-current/', views.set_current_version, name='set_current_version'),


    # ====================================
    # CODE EXPLANATIONS (SUPERUSER-ONLY)
    # ====================================

    # Code explanations
    path('code/', views.code_index, name='code_index'),
    path('code/<slug:slug>/', views.code_detail, name='code_detail'),
    path('code/module/<str:module>/', views.code_by_module, name='code_by_module'),

    # Code management (superuser-only)
    path('admin/code/create/', views.create_code_explanation, name='create_code_explanation'),
    path('admin/code/<int:code_id>/edit/', views.edit_code_explanation, name='edit_code_explanation'),
    path('admin/code/<int:code_id>/delete/', views.delete_code_explanation, name='delete_code_explanation'),


    # ====================================
    # DEVELOPER CHAT (PERMISSION-REQUIRED)
    # ====================================

    # Discussion threads
    path('dev/chat/', views.dev_chat_list, name='dev_chat_list'),
    path('dev/chat/create/', views.create_thread, name='create_thread'),
    path('dev/chat/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('dev/chat/<int:thread_id>/edit/', views.edit_thread, name='edit_thread'),
    path('dev/chat/<int:thread_id>/resolve/', views.resolve_thread, name='resolve_thread'),
    path('dev/chat/<int:thread_id>/archive/', views.archive_thread, name='archive_thread'),

    # Chat messages (AJAX endpoints)
    path('dev/chat/<int:thread_id>/messages/', views.get_messages, name='get_messages'),
    path('dev/chat/<int:thread_id>/post/', views.post_message, name='post_message'),
    path('dev/chat/message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('dev/chat/message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]
