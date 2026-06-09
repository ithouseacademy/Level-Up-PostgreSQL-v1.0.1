from django.urls import path
from . import views
from django.urls import path
from .views import google_verification

urlpatterns = [
      path(
        "google503f1d0f4a7d9466.html",
        google_verification
    ),
    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # ASOSIY SAHIFALAR
    path('', views.home, name='home'),
    path('sayt-haqida/', views.sayt_haqida, name='sayt_haqida'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # ADMIN PANEL
    path('admin-panel/', views.admin_panel, name='admin_panel'),

    # GROUP
    path('group/<int:pk>/', views.group_detail, name='group_detail'),
    path('group/add/', views.group_add, name='group_add'),
    path('group/edit/<int:pk>/', views.group_edit, name='group_edit'),
    path('group/delete/<int:pk>/', views.group_delete, name='group_delete'),

    # KATEGORIYALAR
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # PAPKALAR (FOLDERS)
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/add/', views.folder_add, name='folder_add'),
    path('folders/<int:pk>/edit/', views.folder_edit, name='folder_edit'),
    path('folders/<int:pk>/delete/', views.folder_delete, name='folder_delete'),
    path('folders/<int:folder_id>/categories/', views.folder_categories_manage, name='folder_categories_manage'),
    path('folders/<int:folder_id>/categories/add/', views.folder_category_add, name='folder_category_add'),
    path('folders/categories/remove/<int:folder_category_id>/', views.folder_category_remove, name='folder_category_remove'),
    path('groups/<int:group_id>/folders/', views.group_folders_manage, name='group_folders_manage'),
    path('groups/<int:group_id>/folders/add/', views.group_folder_add, name='group_folder_add'),
    path('groups/folders/remove/<int:group_folder_id>/', views.group_folder_remove, name='group_folder_remove'),
    path('groups/folder-group-config/edit/<int:config_id>/', views.folder_group_config_edit_api, name='folder_group_config_edit_api'),

    # GURUH KATEGORIYALARI
    path('groups/<int:group_id>/categories/', views.group_categories_manage, name='group_categories_manage'),
    path('groups/<int:group_id>/categories/add/', views.group_category_add, name='group_category_add'),
    path('groups/categories/remove/<int:group_category_id>/', views.group_category_remove, name='group_category_remove'),
    path('quiz/student-attempts/<int:student_id>/', views.student_attempts_api, name='student_attempts_api'),
    path('quiz/result-details/<int:result_id>/', views.quiz_result_details_api, name='quiz_result_details_api'),
    path('groups/api/group/<int:group_id>/', views.get_group_api, name='get_group_api'),
    path('groups/category-group-config/edit/<int:config_id>/', views.category_group_config_edit_api, name='category_group_config_edit_api'),
    path('groups/category-group-config/delete/<int:config_id>/', views.category_group_config_delete_api, name='category_group_config_delete_api'),
    path('save-answer-api/', views.save_answer_api, name='save_answer_api'),
    
    # Qadimgi URL'lar uchun (slash boshida)
    path('check-audio-play/', views.check_audio_play_old, name='check_audio_play_old'),
    path('record-audio-play/', views.record_audio_play_old, name='record_audio_play_old'),
    
    path('quiz/auto-stop/', views.auto_stop_exam_api, name='auto_stop_exam_api'),
    path('quiz/check-time-expired/', views.check_time_expired_api, name='check_time_expired_api'),
    
    
    path('categories/<int:category_id>/questions/', views.category_questions_list, name='category_questions_list'),
    path('categories/<int:category_id>/questions/add/', views.category_question_add, name='category_question_add'),
    path('questions/<int:question_id>/edit/', views.category_question_edit, name='category_question_edit'),
    path('questions/<int:question_id>/delete/', views.category_question_delete, name='category_question_delete'),
    path('save-category-configs/<int:group_id>/', views.save_category_configs_api, name='save_category_configs_api'),
    path('quiz/results/<int:group_id>/', views.quiz_results, name='quiz_results'),
    path('category/<int:category_id>/group-config/', views.category_group_config, name='category_group_config'),
    path('category/<int:category_id>/group-config/add/', views.category_group_config_add, name='category_group_config_add'),
    path('category-group-config/<int:config_id>/edit/', views.category_group_config_edit, name='category_group_config_edit'),
    path('category-group-config/<int:config_id>/delete/', views.category_group_config_delete, name='category_group_config_delete'),
    
    # STUDENTLAR
    path('users/', views.student_list, name='student_list'),
    path('user/add/', views.student_add, name='student_add'),
    path('user/edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('user/delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('user/<int:pk>/detail/', views.student_detail, name='student_detail'),
    path('user/<int:pk>/archive/', views.student_archive, name='student_archive'),
    path('user/<int:pk>/restore/', views.student_restore, name='student_restore'),
    path('users/bulk-delete/', views.student_bulk_delete, name='student_bulk_delete'),
    path('users/bulk-archive/', views.student_bulk_archive, name='student_bulk_archive'),

    # STUDENT PANEL
    path('student-panel/', views.student_panel, name='student_panel'),
    path('api/change-group/', views.change_group_api, name='change_group_api'),
    path('api/accept-rules/', views.accept_rules_api, name='accept_rules_api'),


    # ADMIN BOSHQARUVI
    path('make-admin/', views.make_admin, name='make_admin'),
    path('admin-list/', views.admin_list, name='admin_list'),
    path('admin-add/', views.admin_add, name='admin_add'),
    path('admin-edit/<int:admin_id>/', views.admin_edit, name='admin_edit'),
    path('admin-delete/<int:user_id>/', views.admin_delete, name='admin_delete'),

    # QUIZ ADMIN
    path('quiz/admin/', views.quiz_admin, name='quiz_admin'),
    path('quiz/add/', views.quiz_add_question, name='quiz_add_question'),
    path('quiz/edit/<int:question_id>/', views.quiz_edit_question, name='quiz_edit_question'),
    path('quiz/delete/<int:question_id>/', views.quiz_delete_question, name='quiz_delete_question'),

    # QUIZ SESSION
    path('quiz/start/', views.start_exam_api, name='start_exam_api'),
    path('quiz/stop/', views.stop_exam_api, name='stop_exam_api'),
    path('quiz/check/', views.check_exam_api, name='check_exam_api'), 
    path('quiz/check-status/', views.quiz_check_status, name='quiz_check_status'),

    # STUDENT QUIZ
    path('quiz/take/<int:group_id>/', views.quiz_take, name='quiz_take'),
    path('quiz/submit/', views.quiz_submit, name='quiz_submit'),

    # IMTIHON BOSHQARUVI
    path('exam/control/<int:group_id>/', views.exam_control, name='exam_control'),

    # GURUH IMTIHON SOZLAMALARI
    path('group/exam-config/<int:group_id>/', views.group_exam_config, name='group_exam_config'),
    path('group/questions-preview/<int:group_id>/', views.group_questions_preview, name='group_questions_preview'),

    # QOIDALAR
    path('rules-edit/', views.rules_edit, name='rules_edit'),

    # API
    path('api/admin-detail/<int:admin_id>/', views.admin_detail_api, name='admin_detail_api'),
    path('api/admin-update/', views.admin_update, name='admin_update'),
    path('quiz/check-audio-play/', views.check_audio_play_api, name='check_audio_play'),
    path('quiz/record-audio-play/', views.record_audio_play_api, name='record_audio_play'),
    path('api/admin-get-plain-password/<int:admin_id>/', views.admin_get_plain_password, name='admin_get_plain_password'),
    path('api/admin-update-password/', views.admin_update_password, name='admin_update_password'),
    path('reading-texts/', views.reading_texts_list, name='reading_texts_list'),
    path('reading-texts/edit/<int:pk>/', views.reading_text_edit, name='reading_text_edit'),
    
    # SAVOLLAR UCHUN MAXSUS SAHIFALAR
    path('questions-list/', views.admin_question_list, name='admin_question_list'),
    path('questions-add/', views.admin_question_add, name='admin_question_add'),
    path('questions-edit/<int:pk>/', views.admin_question_edit, name='admin_question_edit'),
    path('questions-delete/<int:pk>/', views.admin_question_delete, name='admin_question_delete'),
    # WRITING (Yozma ish) BAHOLASH
    path('writing/review/<int:group_id>/', views.admin_writing_review, name='admin_writing_review'),
    path('writing/grade/<int:result_id>/<int:question_id>/', views.admin_writing_grade_api, name='admin_writing_grade_api'),
    path('quiz/pause/', views.pause_exam_api, name='pause_exam_api'),
    path('quiz/resume/', views.resume_exam_api, name='resume_exam_api'),
    path('quiz/admin-questions/delete/<int:pk>/', views.admin_question_delete_api, name='admin_question_delete_api'),
    path('offline/', views.offline_view, name='offline'),
    path('admin/questions/delete/<int:pk>/', views.admin_question_delete, name='admin_question_delete'),
    path('quiz/get-remaining-time/', views.get_remaining_time_api, name='get_remaining_time_api'),
    path('quiz-submit/', views.quiz_submit, name='quiz_submit'),

    # SPEAKING (Og'zaki) BAHOLASH
    path('speaking/review/<int:group_id>/', views.speaking_review, name='speaking_review'),
    path('speaking/save-score/', views.speaking_save_score_api, name='speaking_save_score_api'),

    # NATIJALARNI EXPORT
    path('quiz/export-csv/<int:group_id>/', views.export_results_csv, name='export_results_csv'),
    path('quiz/export-excel/<int:group_id>/', views.export_results_excel, name='export_results_excel'),

    # STATISTIKA
    path('quiz/statistics/<int:group_id>/', views.quiz_statistics, name='quiz_statistics'),

    # QURILMA NAZORATI
    path('device/monitor/', views.device_monitor, name='device_monitor'),
    path('device/history/', views.device_history, name='device_history'),
    path('device/register/', views.device_register_api, name='device_register'),
    path('device/offline/', views.device_offline_api, name='device_offline'),
    path('device/rename/', views.device_rename_api, name='device_rename'),
    path('device/delete/', views.device_delete_api, name='device_delete'),

    # O'QITUVCHI
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/panel/', views.teacher_panel, name='teacher_panel'),
    path('teacher/group/<int:group_id>/', views.teacher_group_view, name='teacher_group_view'),
    path('teacher/score-logs/', views.teacher_score_logs, name='teacher_score_logs'),
    path('teacher/list/', views.teacher_list, name='teacher_list'),
    path('teacher/add/', views.teacher_add, name='teacher_add'),
    path('teacher/edit/<int:teacher_id>/', views.teacher_edit, name='teacher_edit'),
    path('teacher/delete/<int:teacher_id>/', views.teacher_delete, name='teacher_delete'),

    # ARXIV
    path('results/archive/', views.results_archive, name='results_archive'),

    # SERTIFIKATLAR
    path('certificate/settings/', views.certificate_settings, name='certificate_settings'),
    path('certificate/list/', views.certificate_list, name='certificate_list'),
    path('certificate/view/<int:cert_id>/', views.view_certificate, name='view_certificate'),

    path('certificate/my-certificates/', views.my_certificates, name='my_certificates'),
    path('sertivkat/', views.sertivkat_view, name='sertivkat_view'),
    path('certificate/archive/', views.certificate_archive, name='certificate_archive'),

]