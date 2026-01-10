from django.urls import path
from . import views
urlpatterns = [
    path('admin-home/', views.index_view, name='administrator'),
    path('manage-clients/', views.manage_clients_view, name='manage-clients'),
    path('manage-payments/', views.manage_payments_view, name='manage-payments'),
    path('manage-users/', views.manage_users_view, name='manage-users'),
    path('manage-tutors/', views.manage_tutors_view, name='manage-tutors'),
    path('approve-user/<int:id>/', views.approve_user, name='approve-user'),
    path('disapprove-user/<int:id>/', views.disapprove_user, name='disapprove-user'),
    path('delete-user/<int:id>/', views.delete_user, name='delete-user'),
    path('manage-subjects/', views.manage_subjects_view, name='manage-subjects'),
    path('add-learner/', views.add_learner_view, name='add-learner'),
    path('update-learner/<int:id>/', views.update_learner_view, name='update-learner'),
    path('delete-learner/<int:id>/', views.delete_learner_view, name='delete-learner'),
    path('manage-learners/', views.manage_learners_view, name='manage-learners'),
    path('manage-classes/', views.manage_classes_view, name='manage-classes'),
    path('manage-class-learners/<int:id>/', views.manage_class_learners_view, name='manage-class-learners'),
    path('manage-tutor-payments/', views.manage_tutor_payments_view, name='manage-tutor-payments'),
    path('past-papers/upload/', views.upload_past_paper, name='upload_past_paper'),
]
