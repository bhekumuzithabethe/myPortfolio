# tutor/tests/test.py
"""
Comprehensive test suite for tutor app
"""
import os
from datetime import datetime, time
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import IntegrityError
from django.test import Client as TestClient  # Rename to avoid conflict

from tutor.models import Subject, Class, ClassLearners, Client, Payment, Month, Quiz, Question, Answer, Referrer
from tutor.forms import SubjectForm, ClassForm, ClassLearnersForm, PaymentForm, ClientForm, ReferrerForm, QuizForm, QuestionForm
from administration.models import Learner

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup"""
    def setUp(self):
        # Create admin user (for some tests)
        try:
            self.admin_user = User.objects.create_superuser(
                email='admin@test.com',
                password='adminpass123',
                first_name='Admin',
                last_name='User',
                user_type='Admin',
                approved='Yes'
            )
        except TypeError:
            self.admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='adminpass123',
                first_name='Admin',
                last_name='User',
                user_type='Admin',
                approved='Yes'
            )
        
        # Create regular tutor user
        try:
            self.tutor_user = User.objects.create_user(
                email='tutor@test.com',
                password='tutorpass123',
                first_name='Math',
                last_name='Tutor',
                user_type='Tutor',
                approved='Yes'
            )
        except TypeError:
            self.tutor_user = User.objects.create_user(
                username='tutor',
                email='tutor@test.com',
                password='tutorpass123',
                first_name='Math',
                last_name='Tutor',
                user_type='Tutor',
                approved='Yes'
            )
        
        # Create regular learner user
        try:
            self.learner_user = User.objects.create_user(
                email='learner@test.com',
                password='learnerpass123',
                first_name='John',
                last_name='Doe',
                user_type='Learner',
                approved='Yes'
            )
        except TypeError:
            self.learner_user = User.objects.create_user(
                username='learner',
                email='learner@test.com',
                password='learnerpass123',
                first_name='John',
                last_name='Doe',
                user_type='Learner',
                approved='Yes'
            )
        
        # Create subjects
        self.subject1 = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10',
            tutor=self.tutor_user
        )
        
        self.subject2 = Subject.objects.create(
            name='Physics',
            grade='Grade 10',
            tutor=self.tutor_user
        )
        
        self.subject3 = Subject.objects.create(
            name='Chemistry',
            grade='Grade 11',
            tutor=self.tutor_user
        )
        
        # Create class - using correct fields from your model
        # Note: Based on your model, lesson_time is a TimeField
        self.class_instance = Class.objects.create(
            tutor=self.tutor_user,
            subject=self.subject1,
            grade='Grade 10',
            class_name='Math Class 10A',
            lesson_time=time(9, 0),  # Use time object
            lesson_days='Monday, Wednesday, Friday',
            google_meet_link='https://meet.google.com/abc-defg-hij'
        )
        
        # Create learner instance (for administration app)
        self.learner = Learner.objects.create(
            learner=self.learner_user,
            tutor1=self.tutor_user,
            grade='Grade 10',
            subject1=self.subject1
        )
        
        # Create month for payment tests
        now = datetime.now()
        self.month_name = now.strftime("%B %Y")
        self.month = Month.objects.create(current_month=self.month_name)
        
        self.client = TestClient()  # Use renamed TestClient


# ============================================
# MODEL TESTS
# ============================================

class SubjectModelTests(BaseTestCase):
    """Tests for Subject model"""
    
    def test_subject_creation(self):
        """Test creating a Subject instance"""
        self.assertEqual(self.subject1.name, 'Mathematics')
        self.assertEqual(self.subject1.grade, 'Grade 10')
        self.assertEqual(self.subject1.tutor, self.tutor_user)
    
    def test_subject_string_representation(self):
        """Test __str__ method of Subject model"""
        expected_str = f'Subject: {self.subject1.name} - Grade: {self.subject1.grade} - Tutor: {self.tutor_user.first_name} {self.tutor_user.last_name}'
        self.assertEqual(str(self.subject1), expected_str)
    
    def test_subject_grade_choices(self):
        """Test grade field choices"""
        grade_choices = dict(self.subject1._meta.get_field('grade').choices)
        
        self.assertIn('Grade 1', grade_choices)
        self.assertIn('Grade 12', grade_choices)
        self.assertEqual(grade_choices['Grade 10'], 'Grade 10')
        
        # Check empty choice
        self.assertIn('', grade_choices)
        self.assertEqual(grade_choices[''], '----Select----')


class ClassModelTests(BaseTestCase):
    """Tests for Class model"""
    
    def test_class_creation(self):
        """Test creating a Class instance"""
        self.assertEqual(self.class_instance.class_name, 'Math Class 10A')
        self.assertEqual(self.class_instance.subject, self.subject1)
        self.assertEqual(self.class_instance.grade, 'Grade 10')
        self.assertEqual(self.class_instance.tutor, self.tutor_user)
        self.assertEqual(self.class_instance.google_meet_link, 'https://meet.google.com/abc-defg-hij')
        self.assertEqual(self.class_instance.lesson_time, time(9, 0))
        self.assertEqual(self.class_instance.lesson_days, 'Monday, Wednesday, Friday')
    
    def test_class_string_representation(self):
        """Test __str__ method of Class model"""
        expected_str = f'Class: {self.class_instance.class_name} - Subject: {self.subject1.name} - Tutor: {self.tutor_user.first_name} {self.tutor_user.last_name}'
        self.assertEqual(str(self.class_instance), expected_str)
    
    def test_class_optional_fields(self):
        """Test that optional fields can be null"""
        class_instance = Class.objects.create(
            tutor=self.tutor_user,
            subject=self.subject2,
            grade='Grade 11',
            class_name='Physics Class 11',
            # Optional fields not provided
        )
        
        self.assertIsNone(class_instance.google_meet_link)
        self.assertIsNone(class_instance.lesson_time)
        self.assertIsNone(class_instance.lesson_days)


class MonthModelTests(BaseTestCase):
    """Tests for Month model"""
    
    def test_month_creation(self):
        """Test creating a Month instance"""
        self.assertEqual(self.month.current_month, self.month_name)
    
    def test_month_string_representation(self):
        """Test __str__ method of Month model"""
        expected_str = f'Month: {self.month_name}'
        self.assertEqual(str(self.month), expected_str)
    
    def test_month_unique_constraint(self):
        """Test that month names are unique"""
        with self.assertRaises(Exception):
            Month.objects.create(current_month=self.month_name)


# ============================================
# FORM TESTS
# ============================================

class SubjectFormTests(BaseTestCase):
    """Tests for SubjectForm"""
    
    def test_subject_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'name': 'Biology',
            'grade': 'Grade 12',
        }
        
        form = SubjectForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test saving with tutor
        subject = form.save(commit=False)
        subject.tutor = self.tutor_user
        subject.save()
        
        self.assertEqual(subject.name, 'Biology')
        self.assertEqual(subject.grade, 'Grade 12')
        self.assertEqual(subject.tutor, self.tutor_user)
    
    def test_subject_form_invalid_missing_required(self):
        """Test form with missing required fields"""
        form_data = {
            'name': '',  # Empty name
            'grade': 'Grade 12',
        }
        
        form = SubjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_subject_form_custom_label(self):
        """Test custom label for name field"""
        form = SubjectForm()
        self.assertEqual(form.fields['name'].label, "Subject Name")


class ClassFormTests(BaseTestCase):
    """Tests for ClassForm"""
    
    def test_class_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'class_name': 'Advanced Math',
            'subject': self.subject1.id,
            'grade': 'Grade 12',
            'lesson_time': '14:00',
            'lesson_days': 'Tuesday, Thursday',
            'google_meet_link': 'https://meet.google.com/xyz-abc-def',
        }
        
        form = ClassForm(data=form_data, tutor=self.tutor_user)
        self.assertTrue(form.is_valid())
        
        # Test saving with tutor
        class_instance = form.save(commit=False)
        class_instance.tutor = self.tutor_user
        class_instance.save()
        
        self.assertEqual(class_instance.class_name, 'Advanced Math')
        self.assertEqual(class_instance.subject, self.subject1)
        self.assertEqual(class_instance.grade, 'Grade 12')
    
    def test_class_form_queryset_filtering(self):
        """Test that subject queryset is filtered by tutor"""
        form = ClassForm(tutor=self.tutor_user)
        
        # Should only include subjects for this tutor
        subject_qs = form.fields['subject'].queryset
        self.assertEqual(subject_qs.count(), 3)  # All 3 subjects belong to tutor_user
        self.assertEqual(subject_qs.first().tutor, self.tutor_user)
    
    def test_class_form_empty_label(self):
        """Test empty label for subject field"""
        form = ClassForm(tutor=self.tutor_user)
        self.assertEqual(form.fields['subject'].empty_label, '--Select--')


class PaymentFormTests(BaseTestCase):
    """Tests for PaymentForm"""
    
    def test_payment_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'referrers_full_name': 'Test Referrer',
            'parents_full_name': 'Parent Name',
            'learners_full_name': 'Learner Name',
            'grade_of_learner': 'Grade 10',
            'leaners_subjects': 'Mathematics',
            'total_number_of_days_learner_does_per_week': 5,
            'number_of_days_you_tutor_per_week': 3,
            'name_of_2nd_tutor': '',
            'name_of_3rd_tutor': '',
            'date_of_payment': '2024-01-15',
            'type_of_subscription': 'Online Tutoring',
            'cost_of_subscription': 1000.00,
            'month_as_active_client': '1st Month',
        }
        
        files = {
            'proof_of_payment': SimpleUploadedFile(
                "proof.pdf",
                b"proof content",
                content_type="application/pdf"
            )
        }
        
        form = PaymentForm(form_data, files)
        self.assertTrue(form.is_valid())
    
    def test_payment_form_file_validation(self):
        """Test file validation in payment form"""
        form_data = {
            'referrers_full_name': 'Test Referrer',
            'parents_full_name': 'Parent Name',
            'learners_full_name': 'Learner Name',
            'grade_of_learner': 'Grade 10',
            'leaners_subjects': 'Mathematics',
            'total_number_of_days_learner_does_per_week': 5,
            'number_of_days_you_tutor_per_week': 3,
            'date_of_payment': '2024-01-15',
            'type_of_subscription': 'Online Tutoring',
            'cost_of_subscription': 1000.00,
            'month_as_active_client': '1st Month',
        }
        
        # Test with invalid file type
        files = {
            'proof_of_payment': SimpleUploadedFile(
                "proof.exe",
                b"malicious content",
                content_type="application/x-msdownload"
            )
        }
        
        form = PaymentForm(form_data, files)
        self.assertFalse(form.is_valid())
        self.assertIn('proof_of_payment', form.errors)


# ============================================
# VIEW TESTS
# ============================================

class IndexViewTests(BaseTestCase):
    """Tests for index_view"""
    
    def test_index_view_requires_login(self):
        """Test that index view requires authentication"""
        response = self.client.get(reverse('tutor'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_index_view_as_tutor(self):
        """Test index view accessible by tutor"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            # Try with username if email login fails
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('tutor'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/index.html')
        self.assertIn('classes_instance', response.context)


class SubjectViewsTests(BaseTestCase):
    """Tests for subject-related views"""
    
    def test_add_subject_view_get(self):
        """Test GET request to add subject view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('add-subject'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/add_subject.html')
        self.assertIsInstance(response.context['form'], SubjectForm)
    
    def test_add_subject_view_post_valid(self):
        """Test POST request with valid data to add subject"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        subject_count_before = Subject.objects.filter(tutor=self.tutor_user).count()
        
        form_data = {
            'name': 'Biology',
            'grade': 'Grade 12',
        }
        
        response = self.client.post(reverse('add-subject'), form_data)
        
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(response.url, reverse('tutor-manage-subjects'))
        
        subject_count_after = Subject.objects.filter(tutor=self.tutor_user).count()
        self.assertEqual(subject_count_after, subject_count_before + 1)
    
    def test_manage_subjects_view(self):
        """Test manage subjects view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('tutor-manage-subjects'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/manage/manage_subjects.html')
        
        # Should have subjects in context
        subjects_in_context = response.context['subjects']
        self.assertEqual(subjects_in_context.count(), 3)


class ClassViewsTests(BaseTestCase):
    """Tests for class-related views"""
    
    def test_add_class_view_get(self):
        """Test GET request to add class view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('add-class'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/add_class.html')
        self.assertIsInstance(response.context['form'], ClassForm)
    
    def test_add_class_view_post_valid(self):
        """Test POST request with valid data to add class"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        class_count_before = Class.objects.filter(tutor=self.tutor_user).count()
        
        form_data = {
            'class_name': 'Test Class',
            'subject': self.subject1.id,
            'grade': 'Grade 10',
            'lesson_time': '10:00',
            'lesson_days': 'Monday, Wednesday',
            'google_meet_link': 'https://meet.google.com/test',
        }
        
        response = self.client.post(reverse('add-class'), form_data)
        
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(response.url, reverse('tutor-manage-classes'))
        
        class_count_after = Class.objects.filter(tutor=self.tutor_user).count()
        self.assertEqual(class_count_after, class_count_before + 1)
    
    def test_manage_classes_view(self):
        """Test manage classes view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('tutor-manage-classes'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/manage/manage_classes.html')
        
        # Should have classes in context
        classes_in_context = response.context['classes']
        self.assertEqual(classes_in_context.count(), 1)
    
    def test_edit_class_view_get(self):
        """Test GET request to edit class view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('edit-class', args=[self.class_instance.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/edit_class.html')
        self.assertIsInstance(response.context['form'], ClassForm)
        self.assertEqual(response.context['class'], self.class_instance)
    
    def test_delete_class_view_get(self):
        """Test GET request to delete class view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('delete-class', args=[self.class_instance.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/delete_class.html')
        self.assertEqual(response.context['class'], self.class_instance)


class PaymentFormViewTests(BaseTestCase):
    """Tests for payment form view"""
    
    def test_payment_form_view_get(self):
        """Test GET request to payment form view when month exists"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('payment-form'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/payment_form.html')
        self.assertIsInstance(response.context['form'], PaymentForm)
        self.assertEqual(response.context['month_name'], self.month_name)
    
    def test_payment_form_view_get_no_month(self):
        """Test GET request when month doesn't exist"""
        # Delete the month
        Month.objects.all().delete()
        
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('payment-form'))
        
        self.assertEqual(response.status_code, 302)  # Redirect to tutor home
        self.assertEqual(response.url, reverse('tutor'))


class ClientFormViewTests(BaseTestCase):
    """Tests for client form view"""
    
    def test_client_form_view_get(self):
        """Test GET request to client form view when month exists"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('client-form'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/client_form.html')
        self.assertIsInstance(response.context['form'], ClientForm)
        self.assertEqual(response.context['month_name'], self.month_name)
    
    def test_client_form_view_get_no_month(self):
        """Test GET request when month doesn't exist"""
        # Delete the month
        Month.objects.all().delete()
        
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('client-form'))
        
        self.assertEqual(response.status_code, 302)  # Redirect to tutor home
        self.assertEqual(response.url, reverse('tutor'))


class ReferrerFormViewTests(BaseTestCase):
    """Tests for referrer form view"""
    
    def test_referrer_form_view_get(self):
        """Test GET request to referrer form view when month exists"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('referrer-form'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/add_referrer.html')
        self.assertIsInstance(response.context['form'], ReferrerForm)
        self.assertEqual(response.context['month_name'], self.month_name)


class QuizViewsTests(BaseTestCase):
    """Tests for quiz-related views"""
    
    def setUp(self):
        super().setUp()
        # Create a quiz for testing
        self.quiz = Quiz.objects.create(
            subject=self.subject1,
            quiz_title='Math Quiz 1',
            total_marks=100,
            duration=60
        )
    
    def test_add_quiz_view_get(self):
        """Test GET request to add quiz view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('create_quiz'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/forms/add_quiz.html')
        self.assertIsInstance(response.context['form'], QuizForm)
    
    def test_manage_quizzes_view(self):
        """Test manage quizzes view"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        response = self.client.get(reverse('manage_quizzes'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/manage/manage_quizzes.html')
        
        # Should have quizzes in context
        quizzes_in_context = response.context['quizzes']
        self.assertEqual(quizzes_in_context.count(), 1)


# ============================================
# INTEGRATION TESTS
# ============================================

class IntegrationTests(BaseTestCase):
    """Integration tests for complete workflows"""
    
    def test_subject_management_workflow(self):
        """Test complete subject management workflow"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        # 1. Add subject
        form_data = {
            'name': 'History',
            'grade': 'Grade 9',
        }
        
        response = self.client.post(reverse('add-subject'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify subject was added
        subject = Subject.objects.get(name='History', tutor=self.tutor_user)
        self.assertEqual(subject.grade, 'Grade 9')
        
        # 3. Edit subject
        form_data['name'] = 'World History'
        response = self.client.post(reverse('edit-subject', args=[subject.id]), form_data)
        self.assertEqual(response.status_code, 302)
        
        subject.refresh_from_db()
        self.assertEqual(subject.name, 'World History')
    
    def test_class_management_workflow(self):
        """Test complete class management workflow"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        # 1. Add class
        form_data = {
            'class_name': 'Test Workflow Class',
            'subject': self.subject1.id,
            'grade': 'Grade 10',
            'lesson_time': '11:00',
            'lesson_days': 'Tuesday, Thursday',
            'google_meet_link': 'https://meet.google.com/workflow',
        }
        
        response = self.client.post(reverse('add-class'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify class was added
        class_instance = Class.objects.get(class_name='Test Workflow Class', tutor=self.tutor_user)
        self.assertEqual(class_instance.subject, self.subject1)
        
        # 3. Edit class
        form_data['class_name'] = 'Updated Workflow Class'
        response = self.client.post(reverse('edit-class', args=[class_instance.id]), form_data)
        self.assertEqual(response.status_code, 302)
        
        class_instance.refresh_from_db()
        self.assertEqual(class_instance.class_name, 'Updated Workflow Class')


# ============================================
# PERMISSION TESTS
# ============================================

class PermissionTests(TestCase):
    """Tests for permission requirements"""
    
    def setUp(self):
        # Create tutor user
        try:
            self.tutor_user = User.objects.create_user(
                email='tutor@test.com',
                password='tutorpass123',
                first_name='Math',
                last_name='Tutor',
                user_type='Tutor',
                approved='Yes'
            )
        except TypeError:
            self.tutor_user = User.objects.create_user(
                username='tutor',
                email='tutor@test.com',
                password='tutorpass123',
                first_name='Math',
                last_name='Tutor',
                user_type='Tutor',
                approved='Yes'
            )
        
        # Create another tutor user
        try:
            self.other_tutor = User.objects.create_user(
                email='other@test.com',
                password='otherpass123',
                first_name='Other',
                last_name='Tutor',
                user_type='Tutor',
                approved='Yes'
            )
        except TypeError:
            self.other_tutor = User.objects.create_user(
                username='other',
                email='other@test.com',
                password='otherpass123',
                first_name='Other',
                last_name='Tutor',
                user_type='Tutor',
                approved='Yes'
            )
        
        # Create subject for first tutor
        self.subject = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10',
            tutor=self.tutor_user
        )
        
        # Create class for first tutor
        self.class_instance = Class.objects.create(
            tutor=self.tutor_user,
            subject=self.subject,
            grade='Grade 10',
            class_name='Math Class'
        )
        
        self.client = TestClient()  # Use renamed TestClient
    
    def test_tutor_can_only_access_own_subjects(self):
        """Test that a tutor can only see and edit their own subjects"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        # Should see their subject
        response = self.client.get(reverse('tutor-manage-subjects'))
        subjects = response.context['subjects']
        self.assertEqual(subjects.count(), 1)
        self.assertEqual(subjects.first().tutor, self.tutor_user)
    
    def test_tutor_cannot_access_other_tutor_subjects(self):
        """Test that a tutor cannot edit another tutor's subjects"""
        # Try different login methods
        success = self.client.login(username='other@test.com', password='otherpass123')
        if not success:
            self.client.login(username='other', password='otherpass123')
        
        # Try to access first tutor's subject edit page
        response = self.client.get(reverse('edit-subject', args=[self.subject.id]))
        
        # Should get 404 or redirect (since subject doesn't belong to this tutor)
        self.assertIn(response.status_code, [404, 302, 403])
    
    def test_tutor_can_only_access_own_classes(self):
        """Test that a tutor can only see and edit their own classes"""
        # Try different login methods
        success = self.client.login(username='tutor@test.com', password='tutorpass123')
        if not success:
            self.client.login(username='tutor', password='tutorpass123')
        
        # Should see their class
        response = self.client.get(reverse('tutor-manage-classes'))
        classes = response.context['classes']
        self.assertEqual(classes.count(), 1)
        self.assertEqual(classes.first().tutor, self.tutor_user)
    
    def test_tutor_cannot_access_other_tutor_classes(self):
        """Test that a tutor cannot edit another tutor's classes"""
        # Try different login methods
        success = self.client.login(username='other@test.com', password='otherpass123')
        if not success:
            self.client.login(username='other', password='otherpass123')
        
        # Try to access first tutor's class edit page
        response = self.client.get(reverse('edit-class', args=[self.class_instance.id]))
        
        # Should get 404 or redirect (since class doesn't belong to this tutor)
        self.assertIn(response.status_code, [404, 302, 403])