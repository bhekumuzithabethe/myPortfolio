from django.urls import path
from . import views
urlpatterns = [
    path('learner-home/', views.index_view, name='learner'),
    path('tests-and-quizzes/',views.view_quizzes_view,name="view-quizzes"),
    path('quiz/<int:quiz_id>/question/<int:question_id>/', views.take_question, name='take_question'),
    path('quiz/<int:quiz_id>/question/<int:question_id>/submit/', views.submit_answer, name='submit_answer'),
    path('quiz/<int:quiz_id>/finish/', views.finish_quiz, name='finish_quiz'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('past-papers/', views.past_papers_subjects_view, name='past_papers_subjects'),
    path('past-papers/<int:subject_id>/', views.past_papers_years_view, name='past_papers_years'),
    path('past-papers/<int:subject_id>/<int:year>/', views.past_papers_list_view, name='past_papers_list'),

]
