# tests.py - CORRECTED VERSION
import sys
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

# Import your models
from authentication.models import User
from tutor.models import Quiz, Question, Answer, Subject
from administration.models import Learner, PastQuestionPaper
from learner.models import QuizAttempt, UserAnswer


# ==================== CONFIGURATION ====================
# Override settings for testing
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}
settings.PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


# ==================== MODEL TESTS ====================
class QuizAppModelsTestCase(TestCase):
    """Test QuizApp models"""
    
    def setUp(self):
        # Create users
        self.student = User.objects.create_user(
            username='student1',
            email='student@test.com',
            password='password123',
            user_type=1,  # Learner
            first_name='Student',
            last_name='One'
        )
        
        self.tutor = User.objects.create_user(
            username='tutor1',
            email='tutor@test.com',
            password='password123',
            user_type=2,  # Tutor
            first_name='Tutor',
            last_name='One'
        )
        
        # Create subject with correct field name 'name'
        self.subject = Subject.objects.create(
            name='Mathematics',
            tutor=self.tutor,
            grade='Grade 10'
        )
        
        # Create quiz - with correct fields from your model
        self.quiz = Quiz.objects.create(
            quiz_title='Test Quiz',
            subject=self.subject,
            total_marks=10,
            duration=30  # duration in minutes
        )
        
        # Create question
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_number=1,
            question='What is 2+2?',
            question_type=1,  # Multiple Choice
            mark=5.00
        )
        
        # Create answers
        self.correct_answer = Answer.objects.create(
            question=self.question,
            answer='4',
            is_right=True
        )
        self.wrong_answer = Answer.objects.create(
            question=self.question,
            answer='5',
            is_right=False
        )
        
        # Create learner with correct field names
        self.learner = Learner.objects.create(
            learner=self.student,
            tutor1=self.tutor,
            grade='Grade 10',
            subject1=self.subject
        )
    
    def test_quiz_attempt_creation(self):
        """Test QuizAttempt model"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz,
            total_score=15.50,
            is_completed=True
        )
        
        self.assertEqual(attempt.user.username, 'student1')
        self.assertEqual(attempt.quiz.quiz_title, 'Test Quiz')
        self.assertEqual(attempt.total_score, 15.50)
        self.assertTrue(attempt.is_completed)
        self.assertIsNotNone(attempt.started_at)
    
    def test_unique_constraint_quiz_attempt(self):
        """Test unique together constraint for QuizAttempt"""
        QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        # Attempt to create duplicate
        with self.assertRaises(Exception):
            QuizAttempt.objects.create(
                user=self.student,
                quiz=self.quiz
            )
    
    def test_user_answer_creation(self):
        """Test UserAnswer model"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question,
            user_answer='4',
            is_correct=True,
            marks_awarded=5.00
        )
        
        self.assertEqual(user_answer.user_answer, '4')
        self.assertTrue(user_answer.is_correct)
        self.assertEqual(user_answer.marks_awarded, 5.00)
    
    def test_user_answer_auto_mark_multiple_choice_correct(self):
        """Test auto marking for correct multiple choice answer"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question,
            user_answer=str(self.correct_answer.id)
        )
        
        # Test correct answer
        result = user_answer.auto_mark()
        self.assertTrue(result)
        self.assertTrue(user_answer.is_correct)
        self.assertEqual(user_answer.marks_awarded, 5.00)
        self.assertFalse(user_answer.needs_marking)
    
    def test_user_answer_auto_mark_multiple_choice_wrong(self):
        """Test auto marking for wrong multiple choice answer"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question,
            user_answer=str(self.wrong_answer.id)
        )
        
        result = user_answer.auto_mark()
        self.assertTrue(result)
        self.assertFalse(user_answer.is_correct)
        self.assertEqual(user_answer.marks_awarded, 0)
        self.assertFalse(user_answer.needs_marking)
    
    def test_user_answer_auto_mark_multiple_choice_invalid_id(self):
        """Test auto marking with invalid answer ID"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question,
            user_answer='invalid_id'
        )
        
        result = user_answer.auto_mark()
        self.assertTrue(result)
        self.assertFalse(user_answer.is_correct)
        self.assertEqual(user_answer.marks_awarded, 0)
    
    def test_user_answer_auto_mark_true_false(self):
        """Test auto marking for True/False questions"""
        tf_question = Question.objects.create(
            quiz=self.quiz,
            question_number=2,
            question='Is the sky blue?',
            question_type=2,  # True/False
            mark=2.00
        )
        
        Answer.objects.create(
            question=tf_question,
            answer='True',
            is_right=True
        )
        
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        # Test correct answer
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=tf_question,
            user_answer='True'
        )
        result = user_answer.auto_mark()
        self.assertTrue(result)
        self.assertTrue(user_answer.is_correct)
        self.assertEqual(user_answer.marks_awarded, 2.00)
        
        # Test wrong answer
        user_answer2 = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=tf_question,
            user_answer='False'
        )
        result2 = user_answer2.auto_mark()
        self.assertTrue(result2)
        self.assertFalse(user_answer2.is_correct)
        self.assertEqual(user_answer2.marks_awarded, 0)
    
    def test_user_answer_auto_mark_text_answers(self):
        """Test that text answers need manual marking"""
        text_question = Question.objects.create(
            quiz=self.quiz,
            question_number=3,
            question='Explain your answer',
            question_type=3,  # Text answer
            mark=10.00
        )
        
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=text_question,
            user_answer='My explanation'
        )
        
        result = user_answer.auto_mark()
        self.assertFalse(result)
        self.assertTrue(user_answer.needs_marking)
    
    def test_user_answer_auto_mark_other_question_type(self):
        """Test auto marking for other question types"""
        other_question = Question.objects.create(
            quiz=self.quiz,
            question_number=4,
            question='Other type question',
            question_type=5,  # Some other type
            mark=3.00
        )
        
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=other_question,
            user_answer='Answer'
        )
        
        result = user_answer.auto_mark()
        self.assertFalse(result)
    
    def test_quiz_attempt_calculate_score(self):
        """Test score calculation method"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        # Create multiple user answers with different scores
        question2 = Question.objects.create(
            quiz=self.quiz,
            question_number=2,
            question='Second question',
            question_type=1,
            mark=3.00
        )
        
        Answer.objects.create(
            question=question2,
            answer='Correct',
            is_right=True
        )
        
        # Create correct answer for question 1
        UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question,
            user_answer=str(self.correct_answer.id),
            is_correct=True,
            marks_awarded=5.00
        )
        
        # Create incorrect answer for question 2
        UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=question2,
            user_answer='Wrong',
            is_correct=False,
            marks_awarded=0
        )
        
        total = attempt.calculate_score()
        self.assertEqual(total, 5.00)
        self.assertEqual(attempt.total_score, 5.00)
    
    def test_string_representations(self):
        """Test model string representations"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question,
            user_answer='Test'
        )
        
        self.assertEqual(str(attempt), 'student1 - Test Quiz')
        self.assertEqual(str(user_answer), 'student1 - Q1')


# ==================== VIEW TESTS ====================
class QuizAppViewsTestCase(TestCase):
    """Test QuizApp views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='password123',
            user_type=1,
            first_name='Test',
            last_name='Student'
        )
        
        self.tutor = User.objects.create_user(
            username='testtutor',
            email='tutor@test.com',
            password='password123',
            user_type=2,
            first_name='Test',
            last_name='Tutor'
        )
        
        # Create subject with correct field name 'name'
        self.subject = Subject.objects.create(
            name='Science',
            tutor=self.tutor,
            grade='Grade 10'
        )
        
        # Create quiz with correct fields
        self.quiz = Quiz.objects.create(
            quiz_title='Science Quiz',
            subject=self.subject,
            total_marks=10,
            duration=30
        )
        
        # Create questions
        self.question1 = Question.objects.create(
            quiz=self.quiz,
            question_number=1,
            question='MCQ Question',
            question_type=1,
            mark=5.00
        )
        
        self.correct_answer = Answer.objects.create(
            question=self.question1,
            answer='Correct',
            is_right=True
        )
        self.wrong_answer = Answer.objects.create(
            question=self.question1,
            answer='Wrong',
            is_right=False
        )
        
        self.question2 = Question.objects.create(
            quiz=self.quiz,
            question_number=2,
            question='True/False Question',
            question_type=2,
            mark=3.00
        )
        
        Answer.objects.create(
            question=self.question2,
            answer='True',
            is_right=True
        )
        
        # Create learner
        self.learner = Learner.objects.create(
            learner=self.student,
            tutor1=self.tutor,
            grade='Grade 10',
            subject1=self.subject
        )
        
        # Log in student
        self.client.login(username='teststudent', password='password123')
    
    def test_index_view_authenticated(self):
        """Test index view for authenticated learner"""
        response = self.client.get(reverse('learner'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/index.html')
        self.assertIn('classes', response.context)
        self.assertIn('messages', response.context)
    
    def test_index_view_learner_not_enrolled(self):
        """Test index view when learner is not enrolled"""
        # Delete learner
        self.learner.delete()
        
        response = self.client.get(reverse('learner'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/index.html')
        
        # Check for error message
        messages = list(response.context['messages'])
        self.assertTrue(len(messages) > 0)
    
    def test_index_view_unauthenticated(self):
        """Test index view redirects for unauthenticated users"""
        self.client.logout()
        response = self.client.get(reverse('learner'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertIn('/accounts/login/', response.url)
    
    def test_view_quizzes_view(self):
        """Test view_quizzes view"""
        response = self.client.get(reverse('view-quizzes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/view_quizzes.html')
        self.assertIn('quizzes', response.context)
        self.assertIn('learner', response.context)
        
        # Check quizzes in context
        quizzes = response.context['quizzes']
        self.assertEqual(quizzes.count(), 1)
        self.assertEqual(quizzes.first().quiz_title, 'Science Quiz')
    
    def test_view_quizzes_learner_not_enrolled(self):
        """Test view_quizzes when learner is not enrolled"""
        self.learner.delete()
        
        response = self.client.get(reverse('view-quizzes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/view_quizzes.html')
        
        messages = list(response.context['messages'])
        self.assertTrue(len(messages) > 0)
    
    def test_take_question_get(self):
        """Test GET request to take_question view"""
        url = reverse('take_question', args=[self.quiz.id, self.question1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/take_question.html')
        
        # Check context data
        self.assertEqual(response.context['quiz'], self.quiz)
        self.assertEqual(response.context['question'], self.question1)
        self.assertEqual(len(response.context['answers']), 2)
        self.assertEqual(response.context['total_questions'], 2)
        self.assertIn('next_question', response.context)
        self.assertIn('previous_question', response.context)
        self.assertIn('user_answer', response.context)
        self.assertIn('answered_questions', response.context)
    
    def test_take_question_get_nonexistent_quiz(self):
        """Test take_question with non-existent quiz"""
        url = reverse('take_question', args=[999, self.question1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_take_question_get_nonexistent_question(self):
        """Test take_question with non-existent question"""
        url = reverse('take_question', args=[self.quiz.id, 999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_take_question_post_next(self):
        """Test POST request to take_question with next action"""
        url = reverse('take_question', args=[self.quiz.id, self.question1.id])
        data = {
            'answer': str(self.correct_answer.id),
            'action': 'next'
        }
        response = self.client.post(url, data)
        
        # Should redirect to next question
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.question2.id), response.url)
        
        # Verify answer was saved
        attempt = QuizAttempt.objects.get(user=self.student, quiz=self.quiz)
        user_answer = UserAnswer.objects.get(quiz_attempt=attempt, question=self.question1)
        self.assertEqual(user_answer.user_answer, str(self.correct_answer.id))
        self.assertTrue(user_answer.is_correct)
    
    def test_take_question_post_finish(self):
        """Test POST request to take_question with finish action"""
        url = reverse('take_question', args=[self.quiz.id, self.question1.id])
        data = {
            'answer': str(self.correct_answer.id),
            'action': 'finish'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('finish_quiz', response.url)
        
        # Verify quiz attempt is completed
        attempt = QuizAttempt.objects.get(user=self.student, quiz=self.quiz)
        self.assertTrue(attempt.is_completed)
    
    def test_take_question_post_empty_answer(self):
        """Test submitting empty answer"""
        url = reverse('take_question', args=[self.quiz.id, self.question1.id])
        data = {
            'answer': '',
            'action': 'next'
        }
        response = self.client.post(url, data)
        
        # Should redirect back with error
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.question1.id), response.url)
    
    def test_take_question_post_update_existing_answer(self):
        """Test updating existing answer"""
        # Create initial answer
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz
        )
        UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question1,
            user_answer=str(self.wrong_answer.id)
        )
        
        url = reverse('take_question', args=[self.quiz.id, self.question1.id])
        data = {
            'answer': str(self.correct_answer.id),
            'action': 'next'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verify answer was updated
        user_answer = UserAnswer.objects.get(quiz_attempt=attempt, question=self.question1)
        self.assertEqual(user_answer.user_answer, str(self.correct_answer.id))
    
    def test_submit_answer_view_post(self):
        """Test submit_answer view POST request"""
        url = reverse('submit_answer', args=[self.quiz.id, self.question1.id])
        data = {
            'answer': str(self.correct_answer.id),
            'action': 'next'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verify answer was created
        attempt = QuizAttempt.objects.get(user=self.student, quiz=self.quiz)
        self.assertTrue(UserAnswer.objects.filter(quiz_attempt=attempt, question=self.question1).exists())
    
    def test_submit_answer_view_post_empty_answer_not_finish(self):
        """Test submit_answer with empty answer when not finishing"""
        url = reverse('submit_answer', args=[self.quiz.id, self.question1.id])
        data = {
            'answer': '',
            'action': 'next'
        }
        response = self.client.post(url, data)
        
        # Should redirect back
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.question1.id), response.url)
    
    def test_submit_answer_view_post_empty_answer_finish(self):
        """Test submit_answer with empty answer when finishing"""
        url = reverse('submit_answer', args=[self.quiz.id, self.question1.id])
        data = {
            'answer': '',
            'action': 'finish'
        }
        response = self.client.post(url, data)
        
        # Should redirect to finish
        self.assertEqual(response.status_code, 302)
        self.assertIn('finish_quiz', response.url)
    
    def test_submit_answer_view_get(self):
        """Test submit_answer view GET request (should redirect)"""
        url = reverse('submit_answer', args=[self.quiz.id, self.question1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.question1.id), response.url)
    
    def test_finish_quiz_view(self):
        """Test finish_quiz view"""
        # First answer a question
        attempt = QuizAttempt.objects.create(user=self.student, quiz=self.quiz)
        UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question1,
            user_answer=str(self.correct_answer.id),
            is_correct=True,
            marks_awarded=5.00
        )
        
        url = reverse('finish_quiz', args=[self.quiz.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/quiz_result.html')
        
        # Verify attempt is marked as completed
        attempt.refresh_from_db()
        self.assertTrue(attempt.is_completed)
        self.assertIsNotNone(attempt.completed_at)
    
    def test_finish_quiz_view_no_attempt(self):
        """Test finish_quiz when no attempt exists"""
        url = reverse('finish_quiz', args=[self.quiz.id])
        response = self.client.get(url)
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
    
    def test_finish_quiz_view_already_completed(self):
        """Test finish_quiz when already completed"""
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz,
            is_completed=True,
            completed_at=timezone.now()
        )
        
        url = reverse('finish_quiz', args=[self.quiz.id])
        response = self.client.get(url)
        
        # Should redirect to results
        self.assertEqual(response.status_code, 302)
        self.assertIn('quiz_result', response.url)
    
    def test_quiz_result_view(self):
        """Test quiz_result view"""
        # Create completed attempt
        attempt = QuizAttempt.objects.create(
            user=self.student,
            quiz=self.quiz,
            is_completed=True,
            total_score=8.00,
            completed_at=timezone.now()
        )
        
        UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=self.question1,
            user_answer=str(self.correct_answer.id),
            is_correct=True,
            marks_awarded=5.00
        )
        
        url = reverse('quiz_result', args=[self.quiz.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/quiz_result.html')
        self.assertEqual(response.context['quiz_attempt'], attempt)
        self.assertIn('user_answers', response.context)
    
    def test_quiz_result_view_no_attempt(self):
        """Test quiz_result when no attempt exists"""
        url = reverse('quiz_result', args=[self.quiz.id])
        response = self.client.get(url)
        
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
    
    def test_past_papers_subjects_view(self):
        """Test past papers subjects view"""
        response = self.client.get(reverse('past_papers_subjects'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/past_papers_subjects.html')
        self.assertIn('subjects', response.context)
        
        # Should have 1 subject
        subjects = response.context['subjects']
        self.assertEqual(len(subjects), 1)
    
    def test_past_papers_subjects_view_no_learner(self):
        """Test past papers subjects when user is not a learner"""
        self.learner.delete()
        response = self.client.get(reverse('past_papers_subjects'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/past_papers_subjects.html')
    
    def test_past_papers_years_view(self):
        """Test past papers years view"""
        url = reverse('past_papers_years', args=[self.subject.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/past_papers_years.html')
        self.assertEqual(response.context['subject'], self.subject)
        self.assertIn('years', response.context)
    
    def test_past_papers_list_view(self):
        """Test past papers list view"""
        # Create a past paper
        past_paper = PastQuestionPaper.objects.create(
            subject=self.subject,
            year=2023,
            paper_number=1,
            question_file='past_papers/test.pdf',
            memo_file='past_papers/memo.pdf'
        )
        
        url = reverse('past_papers_list', args=[self.subject.id, 2023])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learner/past_papers_list.html')
        self.assertIn('past_papers', response.context)
        self.assertEqual(response.context['year'], 2023)
        self.assertEqual(response.context['subject'], self.subject)
        
        past_papers = response.context['past_papers']
        self.assertEqual(past_papers.count(), 1)
        self.assertEqual(past_papers.first().year, 2023)
    
    def test_permission_access_control_unauthenticated(self):
        """Test that unauthorized access is prevented"""
        # Log out and try to access protected view
        self.client.logout()
        
        # Test index view
        response = self.client.get(reverse('learner'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        
        # Test quiz view
        url = reverse('take_question', args=[self.quiz.id, self.question1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


# ==================== INTEGRATION TESTS ====================
class QuizAppIntegrationTestCase(TestCase):
    """Integration tests for complete quiz flow"""
    
    def setUp(self):
        self.client = Client()
        
        self.student = User.objects.create_user(
            username='integration_test',
            email='integration@test.com',
            password='password123',
            user_type=1,
            first_name='Integration',
            last_name='Test'
        )
        
        self.tutor = User.objects.create_user(
            username='integration_tutor',
            email='tutor@integration.com',
            password='password123',
            user_type=2,
            first_name='Integration',
            last_name='Tutor'
        )
        
        self.subject = Subject.objects.create(
            name='Integration Subject',
            tutor=self.tutor,
            grade='Grade 10'
        )
        
        self.quiz = Quiz.objects.create(
            quiz_title='Integration Quiz',
            subject=self.subject,
            total_marks=20,
            duration=15
        )
        
        # Create multiple questions
        self.mcq_question = Question.objects.create(
            quiz=self.quiz,
            question_number=1,
            question='MCQ Question',
            question_type=1,
            mark=4.00
        )
        
        self.correct_mcq_answer = Answer.objects.create(
            question=self.mcq_question,
            answer='Correct MCQ',
            is_right=True
        )
        self.wrong_mcq_answer = Answer.objects.create(
            question=self.mcq_question,
            answer='Wrong MCQ',
            is_right=False
        )
        
        self.tf_question = Question.objects.create(
            quiz=self.quiz,
            question_number=2,
            question='True/False Question',
            question_type=2,
            mark=3.00
        )
        
        Answer.objects.create(
            question=self.tf_question,
            answer='True',
            is_right=True
        )
        
        self.text_question = Question.objects.create(
            quiz=self.quiz,
            question_number=3,
            question='Text Question',
            question_type=3,
            mark=10.00
        )
        
        self.learner = Learner.objects.create(
            learner=self.student,
            tutor1=self.tutor,
            grade='Grade 10',
            subject1=self.subject
        )
        
        self.client.login(username='integration_test', password='password123')
    
    def test_complete_quiz_flow_all_correct(self):
        """Test complete quiz taking flow with all correct answers"""
        # 1. View quizzes page
        response = self.client.get(reverse('view-quizzes'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Start quiz - first question (MCQ)
        url = reverse('take_question', args=[self.quiz.id, self.mcq_question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # 3. Answer first question correctly
        data = {'answer': str(self.correct_mcq_answer.id), 'action': 'next'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Answer second question (True/False)
        url = reverse('take_question', args=[self.quiz.id, self.tf_question.id])
        data = {'answer': 'True', 'action': 'next'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # 5. Answer third question (Text)
        url = reverse('take_question', args=[self.quiz.id, self.text_question.id])
        data = {'answer': 'My text answer', 'action': 'finish'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # 6. Finish quiz
        url = reverse('finish_quiz', args=[self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # 7. Verify results
        attempt = QuizAttempt.objects.get(user=self.student, quiz=self.quiz)
        self.assertTrue(attempt.is_completed)
        self.assertEqual(attempt.total_score, 7.00)  # MCQ + TF (text not auto-marked)
        
        # 8. View result page
        url = reverse('quiz_result', args=[self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check user answers
        user_answers = UserAnswer.objects.filter(quiz_attempt=attempt)
        self.assertEqual(user_answers.count(), 3)
        
        # Verify auto-marking worked
        mcq_answer = user_answers.get(question=self.mcq_question)
        self.assertTrue(mcq_answer.is_correct)
        self.assertEqual(mcq_answer.marks_awarded, 4.00)
        
        tf_answer = user_answers.get(question=self.tf_question)
        self.assertTrue(tf_answer.is_correct)
        self.assertEqual(tf_answer.marks_awarded, 3.00)
        
        text_answer = user_answers.get(question=self.text_question)
        self.assertTrue(text_answer.needs_marking)
        self.assertEqual(text_answer.marks_awarded, 0)
    
    def test_complete_quiz_flow_with_wrong_answers(self):
        """Test complete quiz flow with wrong answers"""
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(user=self.student, quiz=self.quiz)
        
        # Answer MCQ wrong
        url = reverse('take_question', args=[self.quiz.id, self.mcq_question.id])
        data = {'answer': str(self.wrong_mcq_answer.id), 'action': 'next'}
        response = self.client.post(url, data)
        
        # Answer TF wrong
        url = reverse('take_question', args=[self.quiz.id, self.tf_question.id])
        data = {'answer': 'False', 'action': 'finish'}
        response = self.client.post(url, data)
        
        # Finish quiz
        url = reverse('finish_quiz', args=[self.quiz.id])
        response = self.client.get(url)
        
        # Verify scores
        attempt.refresh_from_db()
        self.assertEqual(attempt.total_score, 0)  # Both answers wrong


# ==================== EDGE CASE TESTS ====================
class QuizAppEdgeCaseTests(TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='edgestudent',
            email='edge@test.com',
            password='password123',
            user_type=1,
            first_name='Edge',
            last_name='Student'
        )
        self.tutor = User.objects.create_user(
            username='edgetutor',
            email='tutor@edge.com',
            password='password123',
            user_type=2,
            first_name='Edge',
            last_name='Tutor'
        )
        self.subject = Subject.objects.create(
            name='Edge Subject',
            tutor=self.tutor,
            grade='Grade 10'
        )
        self.client.login(username='edgestudent', password='password123')
    
    def test_access_nonexistent_quiz(self):
        """Test accessing non-existent quiz"""
        response = self.client.get(reverse('take_question', args=[999, 1]))
        self.assertEqual(response.status_code, 404)
    
    def test_access_nonexistent_question(self):
        """Test accessing non-existent question"""
        # Create a quiz first
        quiz = Quiz.objects.create(
            quiz_title='Edge Quiz',
            subject=self.subject,
            total_marks=10,
            duration=30
        )
        
        # Create learner to access quiz
        Learner.objects.create(
            learner=self.student,
            tutor1=self.tutor,
            grade='Grade 10',
            subject1=self.subject
        )
        
        # Try to access non-existent question
        response = self.client.get(reverse('take_question', args=[quiz.id, 999]))
        self.assertEqual(response.status_code, 404)
    
    def test_malformed_answer_data(self):
        """Test submitting malformed answer data"""
        quiz = Quiz.objects.create(
            quiz_title='Edge Quiz 3',
            subject=self.subject,
            total_marks=10,
            duration=30
        )
        question = Question.objects.create(
            quiz=quiz,
            question_number=1,
            question='Edge question',
            question_type=1,
            mark=5.00
        )
        Answer.objects.create(
            question=question,
            answer='Answer',
            is_right=True
        )
        
        # Create learner to access quiz
        Learner.objects.create(
            learner=self.student,
            tutor1=self.tutor,
            grade='Grade 10',
            subject1=self.subject
        )
        
        # Submit without answer field
        url = reverse('take_question', args=[quiz.id, question.id])
        data = {'action': 'next'}  # No answer field
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect with error


# ==================== DATABASE TESTS ====================
class QuizAppDatabaseTests(TestCase):
    """Test database constraints and relationships"""
    
    def test_cascade_deletes(self):
        """Test cascade delete behavior"""
        # Create full hierarchy
        student = User.objects.create_user(
            username='cascade',
            email='cascade@test.com',
            password='password123',
            user_type=1,
            first_name='Cascade',
            last_name='Student'
        )
        tutor = User.objects.create_user(
            username='cascadetutor',
            email='cascadetutor@test.com',
            password='password123',
            user_type=2,
            first_name='Cascade',
            last_name='Tutor'
        )
        subject = Subject.objects.create(
            name='Cascade Subject',
            tutor=tutor,
            grade='Grade 10'
        )
        quiz = Quiz.objects.create(
            quiz_title='Cascade Quiz',
            subject=subject,
            total_marks=10,
            duration=30
        )
        question = Question.objects.create(
            quiz=quiz,
            question_number=1,
            question='Cascade question',
            question_type=1,
            mark=5.00
        )
        
        # Create quiz attempt and user answer
        attempt = QuizAttempt.objects.create(
            user=student,
            quiz=quiz
        )
        user_answer = UserAnswer.objects.create(
            quiz_attempt=attempt,
            question=question,
            user_answer='Answer'
        )
        
        # Test cascade delete from quiz
        quiz_count_before = Quiz.objects.count()
        attempt_count_before = QuizAttempt.objects.count()
        answer_count_before = UserAnswer.objects.count()
        
        quiz.delete()
        
        # QuizAttempt and UserAnswer should be deleted
        self.assertEqual(Quiz.objects.count(), quiz_count_before - 1)
        self.assertEqual(QuizAttempt.objects.count(), attempt_count_before - 1)
        self.assertEqual(UserAnswer.objects.count(), answer_count_before - 1)
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraint violations"""
        student = User.objects.create_user(
            username='fkstudent',
            email='fk@test.com',
            password='password123',
            user_type=1,
            first_name='FK',
            last_name='Student'
        )
        
        # Try to create QuizAttempt with non-existent quiz
        with self.assertRaises(Exception):
            QuizAttempt.objects.create(
                user=student,
                quiz_id=999  # Non-existent quiz
            )
        
        # Try to create UserAnswer with non-existent question
        tutor = User.objects.create_user(
            username='fktutor',
            email='fktutor@test.com',
            password='password123',
            user_type=2,
            first_name='FK',
            last_name='Tutor'
        )
        subject = Subject.objects.create(
            name='FK Subject',
            tutor=tutor,
            grade='Grade 10'
        )
        quiz = Quiz.objects.create(
            quiz_title='FK Quiz',
            subject=subject,
            total_marks=10,
            duration=30
        )
        attempt = QuizAttempt.objects.create(
            user=student,
            quiz=quiz
        )
        
        with self.assertRaises(Exception):
            UserAnswer.objects.create(
                quiz_attempt=attempt,
                question_id=999,  # Non-existent question
                user_answer='Answer'
            )


# ==================== TEST FOR AUTO-INCREMENT QUESTION NUMBER ====================
class QuestionNumberAutoIncrementTest(TestCase):
    """Test auto-incrementing question numbers per quiz"""
    
    def setUp(self):
        self.tutor = User.objects.create_user(
            username='question_tutor',
            email='tutor@question.com',
            password='password123',
            user_type=2,
            first_name='Question',
            last_name='Tutor'
        )
        self.subject = Subject.objects.create(
            name='Math',
            tutor=self.tutor,
            grade='Grade 10'
        )
        self.quiz = Quiz.objects.create(
            quiz_title='Math Quiz',
            subject=self.subject,
            total_marks=10,
            duration=30
        )
        self.quiz2 = Quiz.objects.create(
            quiz_title='Math Quiz 2',
            subject=self.subject,
            total_marks=10,
            duration=30
        )
    
    def test_auto_increment_first_question(self):
        """Test first question gets number 1"""
        question = Question.objects.create(
            quiz=self.quiz,
            question='First question',
            question_type=1,
            mark=5
        )
        self.assertEqual(question.question_number, 1)
    
    def test_auto_increment_multiple_questions(self):
        """Test multiple questions get sequential numbers"""
        questions = []
        for i in range(5):
            question = Question.objects.create(
                quiz=self.quiz,
                question=f'Question {i+1}',
                question_type=1,
                mark=5
            )
            questions.append(question)
        
        numbers = [q.question_number for q in questions]
        self.assertEqual(numbers, [1, 2, 3, 4, 5])
    
    def test_auto_increment_per_quiz(self):
        """Test numbering is per quiz, not global"""
        # Add questions to first quiz
        q1 = Question.objects.create(quiz=self.quiz, question='Q1', question_type=1, mark=5)
        q2 = Question.objects.create(quiz=self.quiz, question='Q2', question_type=1, mark=5)
        
        # Add question to second quiz
        q3 = Question.objects.create(quiz=self.quiz2, question='Q1', question_type=1, mark=5)
        
        self.assertEqual(q1.question_number, 1)
        self.assertEqual(q2.question_number, 2)
        self.assertEqual(q3.question_number, 1)  # Should start at 1 for new quiz
    
    def test_delete_and_add_new_question(self):
        """Test that deleting and adding new questions works correctly"""
        # Create 3 questions
        q1 = Question.objects.create(quiz=self.quiz, question='Q1', question_type=1, mark=5)
        q2 = Question.objects.create(quiz=self.quiz, question='Q2', question_type=1, mark=5)
        q3 = Question.objects.create(quiz=self.quiz, question='Q3', question_type=1, mark=5)
        
        # Delete question 2
        q2.delete()
        
        # Add new question
        q4 = Question.objects.create(quiz=self.quiz, question='Q4', question_type=1, mark=5)
        
        # Check question numbers
        self.assertEqual(q1.question_number, 1)
        self.assertEqual(q3.question_number, 3)
        self.assertEqual(q4.question_number, 4)  # Should be 4, not 3


# ==================== SIMPLE TEST RUNNER ====================
def run_tests():
    """Simple test runner"""
    import sys
    
    # Test classes to run
    test_classes = [
        QuizAppModelsTestCase,
        QuizAppViewsTestCase,
        QuizAppIntegrationTestCase,
        QuizAppEdgeCaseTests,
        QuizAppDatabaseTests,
        QuestionNumberAutoIncrementTest
    ]
    
    print("Running Quiz App Tests...")
    print("=" * 60)
    
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        if result.failures or result.errors:
            failed_tests.append(test_class.__name__)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if failed_tests:
        print(f"FAILED: {len(failed_tests)} test classes failed")
        print("Failed classes:")
        for test in failed_tests:
            print(f"  - {test}")
        return False
    else:
        print("SUCCESS: All tests passed!")
        return True


if __name__ == '__main__':
    import unittest
    
    # Run the tests
    success = run_tests()
    sys.exit(0 if success else 1)