from django.urls import path
from . import views
urlpatterns = [
    path('tutor-home/', views.index_view, name='tutor'),
    path('payment-form/', views.payment_form_view, name='payment-form'),
    path('client-form/', views.client_form_view, name='client-form'),
    path('referrer-form/', views.referrer_form_view, name='referrer-form'),

    path('create-quiz/',views.add_quiz_view,name="create_quiz"),
    path('update-quiz/<int:id>/',views.edit_quiz_view,name="update_quiz"),
    path('delete-quiz/<int:id>/',views.delete_quiz_view,name="delete_quiz"),
    path('manage-quizzes/',views.manage_quizzes_view,name="manage_quizzes"),

    path('quiz/<int:quiz_id>/add-question/',views.add_question_view,name="create_question"),
    path('update-question/<int:id>/',views.edit_question_view,name="update_question"),
    path('delete-question/<int:id>/',views.delete_question_view,name="delete_question"),
    path('manage-questions/<int:id>/',views.manage_questions_view,name="manage_questions"),


    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chatbot/clear/', views.clear_chat_history, name='clear_chat_history'),
    path('chatbot/export/', views.export_chat_history, name='export_chat_history'),

    path('add-subject/', views.add_subject_view, name='add-subject'),
    path('manage-subjects/', views.manage_subjects_view, name='tutor-manage-subjects'),
    path('edit-subject/<int:id>/', views.edit_subject_view, name='edit-subject'),
    path('delete-subject/<int:id>/', views.delete_subject_view, name='delete-subject'),

    path('add-class/', views.add_class_view, name='add-class'),
    path('manage-classes/', views.manage_classes_view, name='tutor-manage-classes'),
    path('edit-class/<int:id>/', views.edit_class_view, name='edit-class'),
    path('delete-class/<int:id>/', views.delete_class_view, name='delete-class'),

    path('add-class-learners/', views.add_class_learners_view, name='add-class-learners'),
    path('manage-class-learners/<int:id>/', views.manage_class_learners_view, name='tutor-manage-class-learners'),
    path('edit-class-learners/<int:id>/', views.edit_class_learners_view, name='edit-class-learners'),
    path('delete-class-learners/<int:id>/', views.delete_class_learners_view, name='delete-class-learners'),

    path('past-papers/', views.past_papers_subjects_view, name='tutor_past_papers_subjects'),
    path('past-papers/<int:subject_id>/', views.past_papers_years_view, name='tutor_past_papers_years'),
    path('past-papers/<int:subject_id>/<int:year>/', views.past_papers_list_view, name='tutor_past_papers_list'),

]