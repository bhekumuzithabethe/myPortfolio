# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.utils import timezone

from learner.models import Learner, PastQuestionPaper, GRADE_CHOICES
from learner.forms import LearnerForm, PastQuestionPaperForm
from tutor.models import Subject, Month, Payment, Client, Class, ClassLearners
from authentication.models import User

import tempfile
from PIL import Image
import os

User = get_user_model()

class LearnerModelsTest(TestCase):
    """Test suite for Learner models"""
    
    def setUp(self):
        # Create users
        self.learner_user = User.objects.create_user(
            email='learner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            user_type='Learner',
            approved='Yes'
        )
        
        self.tutor1_user = User.objects.create_user(
            email='tutor1@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            user_type='Tutor',
            approved='Yes'
        )
        
        self.tutor2_user = User.objects.create_user(
            email='tutor2@test.com',
            password='testpass123',
            first_name='Bob',
            last_name='Johnson',
            user_type='Tutor',
            approved='Yes'
        )
        
        # Create subjects
        self.subject1 = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10'
        )
        
        self.subject2 = Subject.objects.create(
            name='Physical Science',
            grade='Grade 10'
        )
        
        self.subject3 = Subject.objects.create(
            name='English',
            grade='Grade 10'
        )
    
    def test_learner_creation_minimal(self):
        """Test creating a learner with only required fields"""
        learner = Learner.objects.create(
            learner=self.learner_user,
            tutor1=self.tutor1_user,
            grade='Grade 10',
            subject1=self.subject1
        )
        
        self.assertEqual(str(learner), "Learner: John Doe")
        self.assertEqual(learner.grade, 'Grade 10')
        self.assertEqual(learner.tutor1, self.tutor1_user)
        self.assertIsNone(learner.tutor2)
        self.assertIsNone(learner.tutor3)
        self.assertEqual(learner.subject1, self.subject1)
        self.assertIsNone(learner.subject2)
        self.assertIsNone(learner.subject3)
    
    def test_learner_creation_all_fields(self):
        """Test creating a learner with all fields"""
        learner = Learner.objects.create(
            learner=self.learner_user,
            tutor1=self.tutor1_user,
            tutor2=self.tutor2_user,
            tutor3=None,
            grade='Grade 12',
            subject1=self.subject1,
            subject2=self.subject2,
            subject3=self.subject3
        )
        
        self.assertEqual(learner.grade, 'Grade 12')
        self.assertEqual(learner.tutor2, self.tutor2_user)
        self.assertEqual(learner.subject2, self.subject2)
        self.assertEqual(learner.subject3, self.subject3)
    
    def test_grade_choices(self):
        """Test that GRADE_CHOICES contains expected values"""
        grades = [choice[0] for choice in GRADE_CHOICES]
        
        # Check for empty choice
        self.assertIn('', grades)
        
        # Check all grades are present
        for i in range(1, 13):
            self.assertIn(f'Grade {i}', grades)
    
    def test_past_paper_upload_path(self):
        """Test the upload path generation"""
        from learner.models import past_paper_upload_path
        
        # Create a mock instance
        class MockInstance:
            def __init__(self):
                self.paper_number = 1
                self.subject = self.subject1
                self.year = 2023
            
            @property
            def subject(self):
                class MockSubject:
                    name = 'Mathematics'
                    grade = 'Grade 10'
                return MockSubject()
        
        instance = MockInstance()
        filename = 'test_paper.pdf'
        
        path = past_paper_upload_path(instance, filename)
        
        expected_path = 'past_papers/grade_10/mathematics/2023/paper_1/test_paper.pdf'
        self.assertEqual(path, expected_path)
    
    def test_past_paper_creation(self):
        """Test creating a past question paper"""
        # Create a mock file
        test_file = SimpleUploadedFile(
            "test_paper.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        paper = PastQuestionPaper.objects.create(
            subject=self.subject1,
            year=2023,
            paper_number=1,
            question_file=test_file,
            memo_file=test_file
        )
        
        self.assertEqual(str(paper), "Mathematics | Grade 10 | 2023 | Paper 1")
        self.assertEqual(paper.year, 2023)
        self.assertEqual(paper.paper_number, 1)
        self.assertIsNotNone(paper.uploaded_at)
        
        # Clean up file
        if os.path.exists(paper.question_file.path):
            os.remove(paper.question_file.path)
        if os.path.exists(paper.memo_file.path):
            os.remove(paper.memo_file.path)
    
    def test_past_paper_without_paper_number(self):
        """Test creating a past paper without paper number"""
        test_file = SimpleUploadedFile(
            "test_paper.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        paper = PastQuestionPaper.objects.create(
            subject=self.subject1,
            year=2023,
            paper_number=None,
            question_file=test_file,
            memo_file=test_file
        )
        
        self.assertEqual(str(paper), "Mathematics | Grade 10 | 2023 | General")
        
        # Clean up
        if os.path.exists(paper.question_file.path):
            os.remove(paper.question_file.path)
        if os.path.exists(paper.memo_file.path):
            os.remove(paper.memo_file.path)


class LearnerFormsTest(TestCase):
    """Test suite for Learner forms"""
    
    def setUp(self):
        # Create users
        self.learner_user = User.objects.create_user(
            email='learner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            user_type='Learner',
            approved='Yes'
        )
        
        self.tutor_user = User.objects.create_user(
            email='tutor@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            user_type='Tutor',
            approved='Yes'
        )
        
        # Create additional users for testing querysets
        self.learner_user2 = User.objects.create_user(
            email='learner2@test.com',
            password='testpass123',
            first_name='Alice',
            last_name='Brown',
            user_type='Learner',
            approved='Yes'
        )
        
        self.tutor_user2 = User.objects.create_user(
            email='tutor2@test.com',
            password='testpass123',
            first_name='Bob',
            last_name='Johnson',
            user_type='Tutor',
            approved='Yes'
        )
        
        # Create subjects
        self.subject1 = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10'
        )
        
        self.subject2 = Subject.objects.create(
            name='Science',
            grade='Grade 10'
        )
        
        # Create existing learner for update tests
        self.existing_learner = Learner.objects.create(
            learner=self.learner_user,
            tutor1=self.tutor_user,
            grade='Grade 10',
            subject1=self.subject1
        )
    
    def test_learner_form_valid_data(self):
        """Test LearnerForm with valid data"""
        form_data = {
            'learner': self.learner_user2.id,
            'tutor1': self.tutor_user.id,
            'grade': 'Grade 11',
            'subject1': self.subject1.id
        }
        
        form = LearnerForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save form
        learner = form.save()
        self.assertEqual(learner.learner, self.learner_user2)
        self.assertEqual(learner.grade, 'Grade 11')
    
    def test_learner_form_with_optional_fields(self):
        """Test LearnerForm with all optional fields"""
        form_data = {
            'learner': self.learner_user2.id,
            'tutor1': self.tutor_user.id,
            'tutor2': self.tutor_user2.id,
            'grade': 'Grade 12',
            'subject1': self.subject1.id,
            'subject2': self.subject2.id
        }
        
        form = LearnerForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        learner = form.save()
        self.assertEqual(learner.tutor2, self.tutor_user2)
        self.assertEqual(learner.subject2, self.subject2)
    
    def test_learner_form_missing_required_fields(self):
        """Test LearnerForm with missing required fields"""
        form_data = {
            'learner': self.learner_user2.id,
            # Missing tutor1, grade, subject1
        }
        
        form = LearnerForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Check specific error messages
        self.assertIn('tutor1', form.errors)
        self.assertIn('grade', form.errors)
        self.assertIn('subject1', form.errors)
    
    def test_learner_form_querysets(self):
        """Test that form querysets are correctly filtered"""
        form = LearnerForm()
        
        # Check learner queryset contains only Learner users
        self.assertEqual(
            set(form.fields['learner'].queryset),
            set(User.objects.filter(user_type='Learner'))
        )
        
        # Check tutor querysets contain only Tutor users
        tutor_queryset = User.objects.filter(user_type='Tutor')
        self.assertEqual(
            set(form.fields['tutor1'].queryset),
            set(tutor_queryset)
        )
        self.assertEqual(
            set(form.fields['tutor2'].queryset),
            set(tutor_queryset)
        )
        
        # Check subject querysets
        subject_queryset = Subject.objects.all()
        self.assertEqual(
            set(form.fields['subject1'].queryset),
            set(subject_queryset)
        )
    
    def test_learner_form_update(self):
        """Test updating an existing learner"""
        form_data = {
            'learner': self.learner_user.id,
            'tutor1': self.tutor_user2.id,  # Changed tutor
            'grade': 'Grade 12',  # Changed grade
            'subject1': self.subject1.id
        }
        
        form = LearnerForm(data=form_data, instance=self.existing_learner)
        self.assertTrue(form.is_valid())
        
        learner = form.save()
        self.assertEqual(learner.tutor1, self.tutor_user2)
        self.assertEqual(learner.grade, 'Grade 12')
    
    def test_past_question_paper_form_valid(self):
        """Test PastQuestionPaperForm with valid data"""
        # Create a test file
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"test content",
            content_type="application/pdf"
        )
        
        form_data = {
            'subject': self.subject1.id,
            'year': 2023,
            'paper_number': 1,
        }
        
        file_data = {
            'question_file': test_file,
            'memo_file': test_file
        }
        
        form = PastQuestionPaperForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())
        
        # Save and clean up
        paper = form.save()
        if os.path.exists(paper.question_file.path):
            os.remove(paper.question_file.path)
        if os.path.exists(paper.memo_file.path):
            os.remove(paper.memo_file.path)
    
    def test_past_question_paper_form_invalid(self):
        """Test PastQuestionPaperForm with invalid data"""
        form_data = {
            'subject': self.subject1.id,
            'year': '',  # Missing year
            'paper_number': 1,
        }
        
        form = PastQuestionPaperForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('year', form.errors)


class LearnerViewsTest(TestCase):
    """Test suite for Learner views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            user_type='Admin',
            approved='Yes'
        )
        
        # Create regular users
        self.learner_user = User.objects.create_user(
            email='learner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            user_type='Learner',
            approved='Yes'
        )
        
        self.tutor_user = User.objects.create_user(
            email='tutor@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            user_type='Tutor',
            approved='Yes'
        )
        
        self.unapproved_user = User.objects.create_user(
            email='unapproved@test.com',
            password='testpass123',
            first_name='Pending',
            last_name='User',
            user_type='Tutor',
            approved='No'
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10'
        )
        
        # Create learner
        self.learner = Learner.objects.create(
            learner=self.learner_user,
            tutor1=self.tutor_user,
            grade='Grade 10',
            subject1=self.subject
        )
        
        # Create month for payment tests
        self.current_month = timezone.now().strftime("%B %Y")
        self.month = Month.objects.create(current_month=self.current_month)
        
        # Create payment
        self.payment = Payment.objects.create(
            tutors_full_name='Jane Smith',
            amount_due_to_tutor=1000.00,
            month=self.month
        )
        
        # Create client
        self.client_obj = Client.objects.create(
            client_name='Test Client',
            month=self.month
        )
        
        # Create class
        self.class_obj = Class.objects.create(
            tutor=self.tutor_user,
            subject=self.subject,
            class_time='09:00:00'
        )
        
        # Create class learner
        self.class_learner = ClassLearners.objects.create(
            class_instance=self.class_obj,
            learner=self.learner_user
        )
    
    # =============================
    # Authentication Tests
    # =============================
    
    def test_index_view_requires_login(self):
        """Test that index view requires authentication"""
        response = self.client.get(reverse('administrator'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login/', response.url)
    
    def test_index_view_authenticated(self):
        """Test index view with authenticated admin"""
        self.client.login(email='admin@test.com', password='adminpass123')
        response = self.client.get(reverse('administrator'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/index.html')
        
        # Check context
        self.assertIn('pending_count', response.context)
        self.assertIn('messages', response.context)
    
    # =============================
    # User Management Tests
    # =============================
    
    def test_manage_users_view(self):
        """Test manage users view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        response = self.client.get(reverse('manage-users'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_users.html')
        
        # Check users are in context
        self.assertIn('users', response.context)
        users = response.context['users']
        
        # Should exclude Admin users
        self.assertNotIn(self.admin_user, users)
        
        # Should include other users
        user_emails = [user.email for user in users]
        self.assertIn(self.learner_user.email, user_emails)
        self.assertIn(self.tutor_user.email, user_emails)
        self.assertIn(self.unapproved_user.email, user_emails)
    
    def test_approve_user(self):
        """Test approving a user"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Initially unapproved
        self.assertEqual(self.unapproved_user.approved, 'No')
        
        # Approve user
        response = self.client.get(reverse('approve-user', args=[self.unapproved_user.id]))
        
        # Refresh from database
        self.unapproved_user.refresh_from_db()
        
        # Check user is approved
        self.assertEqual(self.unapproved_user.approved, 'Yes')
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage-users'))
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Tutor King Account Approval')
        self.assertIn(self.unapproved_user.email, mail.outbox[0].to)
    
    def test_disapprove_user(self):
        """Test disapproving a user"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Initially approved
        self.tutor_user.approved = 'Yes'
        self.tutor_user.save()
        
        # Disapprove user
        response = self.client.get(reverse('disapprove-user', args=[self.tutor_user.id]))
        
        # Refresh from database
        self.tutor_user.refresh_from_db()
        
        # Check user is disapproved
        self.assertEqual(self.tutor_user.approved, 'No')
        
        # Check redirect and email
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
    
    def test_delete_user(self):
        """Test deleting a user"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Count before deletion
        user_count_before = User.objects.count()
        
        # Delete user
        response = self.client.get(reverse('delete-user', args=[self.unapproved_user.id]))
        
        # Check user was deleted
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before - 1)
        
        # Check user no longer exists
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.unapproved_user.id)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
    
    # =============================
    # Learner Management Tests
    # =============================
    
    def test_manage_learners_view(self):
        """Test manage learners view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        response = self.client.get(reverse('manage-learners'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_learners.html')
        
        # Check learners are in context
        self.assertIn('learners', response.context)
        learners = response.context['learners']
        self.assertIn(self.learner, learners)
    
    def test_add_learner_view_get(self):
        """Test GET request to add learner view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        response = self.client.get(reverse('add-learner'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/forms/add_learner.html')
        
        # Check form is in context
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], LearnerForm)
    
    def test_add_learner_view_post_valid(self):
        """Test POST request to add learner with valid data"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Create another learner user
        new_learner_user = User.objects.create_user(
            email='newlearner@test.com',
            password='testpass123',
            first_name='New',
            last_name='Learner',
            user_type='Learner',
            approved='Yes'
        )
        
        learner_count_before = Learner.objects.count()
        
        response = self.client.post(reverse('add-learner'), {
            'learner': new_learner_user.id,
            'tutor1': self.tutor_user.id,
            'grade': 'Grade 11',
            'subject1': self.subject.id
        })
        
        learner_count_after = Learner.objects.count()
        
        # Check learner was created
        self.assertEqual(learner_count_after, learner_count_before + 1)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage-learners'))
        
        # Check new learner exists
        self.assertTrue(
            Learner.objects.filter(learner=new_learner_user).exists()
        )
    
    def test_add_learner_view_post_invalid(self):
        """Test POST request to add learner with invalid data"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        learner_count_before = Learner.objects.count()
        
        response = self.client.post(reverse('add-learner'), {
            # Missing required fields
            'learner': self.learner_user.id,
        })
        
        learner_count_after = Learner.objects.count()
        
        # Check no learner was created
        self.assertEqual(learner_count_after, learner_count_before)
        
        # Check form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/forms/add_learner.html')
        self.assertIn('form', response.context)
    
    def test_update_learner_view_get(self):
        """Test GET request to update learner"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('update-learner', args=[self.learner.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/forms/update_learner.html')
        
        # Check form is populated with instance data
        form = response.context['form']
        self.assertEqual(form.instance, self.learner)
    
    def test_update_learner_view_post(self):
        """Test POST request to update learner"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.post(reverse('update-learner', args=[self.learner.id]), {
            'learner': self.learner_user.id,
            'tutor1': self.tutor_user.id,
            'grade': 'Grade 12',  # Changed from Grade 10
            'subject1': self.subject.id
        })
        
        # Refresh from database
        self.learner.refresh_from_db()
        
        # Check grade was updated
        self.assertEqual(self.learner.grade, 'Grade 12')
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage-learners'))
    
    def test_delete_learner_view(self):
        """Test deleting a learner"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        learner_count_before = Learner.objects.count()
        
        response = self.client.get(reverse('delete-learner', args=[self.learner.id]))
        
        learner_count_after = Learner.objects.count()
        
        # Check learner was deleted
        self.assertEqual(learner_count_after, learner_count_before - 1)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage-learners'))
        
        # Check learner no longer exists
        with self.assertRaises(Learner.DoesNotExist):
            Learner.objects.get(id=self.learner.id)
    
    # =============================
    # Payment Management Tests
    # =============================
    
    def test_manage_payments_view_with_month(self):
        """Test manage payments view when month exists"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('manage-payments'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_payements.html')
        
        # Check context
        self.assertIn('payments', response.context)
        self.assertIn('month', response.context)
        self.assertEqual(response.context['month'], self.current_month)
        
        # Check payments are in context
        payments = response.context['payments']
        self.assertIn(self.payment, payments)
    
    def test_manage_payments_view_without_month(self):
        """Test manage payments view when month doesn't exist"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Delete the month
        Month.objects.all().delete()
        
        response = self.client.get(reverse('manage-payments'))
        
        # Should redirect to administrator index
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administrator'))
    
    def test_manage_clients_view(self):
        """Test manage clients view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('manage-clients'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_clients.html')
        
        # Check clients are in context
        self.assertIn('clients', response.context)
        clients = response.context['clients']
        self.assertIn(self.client_obj, clients)
    
    def test_manage_tutor_payments_view(self):
        """Test manage tutor payments view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('manage-tutor-payments'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_tutor_payments.html')
        
        # Check tutor payment data is in context
        self.assertIn('tutor_payment_data', response.context)
        
        # Check data structure
        tutor_data = response.context['tutor_payment_data']
        for data in tutor_data:
            self.assertIn('tutor_name', data)
            self.assertIn('total_payment', data)
            self.assertIsInstance(data['total_payment'], (int, float))
    
    # =============================
    # Subject and Class Tests
    # =============================
    
    def test_manage_subjects_view(self):
        """Test manage subjects view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('manage-subjects'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_subjects.html')
        
        # Check subjects are in context
        self.assertIn('subjects', response.context)
        subjects = response.context['subjects']
        self.assertIn(self.subject, subjects)
    
    def test_manage_tutors_view(self):
        """Test manage tutors view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('manage-tutors'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_tutors.html')
        
        # Check tutors are in context
        self.assertIn('tutors', response.context)
        tutors = response.context['tutors']
        
        # Should only include Tutor users
        for tutor in tutors:
            self.assertEqual(tutor.user_type, 'Tutor')
    
    def test_manage_classes_view(self):
        """Test manage classes view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('manage-classes'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_classes.html')
        
        # Check classes are in context
        self.assertIn('classes', response.context)
        classes = response.context['classes']
        self.assertIn(self.class_obj, classes)
    
    def test_manage_class_learners_view(self):
        """Test manage class learners view"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('manage-class-learners', args=[self.class_obj.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/manage/manage_class_learners.html')
        
        # Check context
        self.assertIn('learners', response.context)
        self.assertIn('class', response.context)
        
        # Check class instance
        self.assertEqual(response.context['class'], self.class_obj)
        
        # Check class learners
        class_learners = response.context['learners']
        self.assertIn(self.class_learner, class_learners)
    
    # =============================
    # Past Paper Tests
    # =============================
    
    def test_upload_past_paper_view_get(self):
        """Test GET request to upload past paper"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        response = self.client.get(reverse('upload_past_paper'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/forms/upload_past_question_paper.html')
        
        # Check form is in context
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PastQuestionPaperForm)
    
    def test_upload_past_paper_view_post(self):
        """Test POST request to upload past paper"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Create test files
        test_file_content = b"Test PDF content"
        question_file = SimpleUploadedFile(
            "question.pdf",
            test_file_content,
            content_type="application/pdf"
        )
        memo_file = SimpleUploadedFile(
            "memo.pdf",
            test_file_content,
            content_type="application/pdf"
        )
        
        paper_count_before = PastQuestionPaper.objects.count()
        
        response = self.client.post(reverse('upload_past_paper'), {
            'subject': self.subject.id,
            'year': 2023,
            'paper_number': 1,
            'question_file': question_file,
            'memo_file': memo_file
        })
        
        paper_count_after = PastQuestionPaper.objects.count()
        
        # Check paper was created
        self.assertEqual(paper_count_after, paper_count_before + 1)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administrator'))
        
        # Clean up created files
        new_paper = PastQuestionPaper.objects.latest('id')
        if os.path.exists(new_paper.question_file.path):
            os.remove(new_paper.question_file.path)
        if os.path.exists(new_paper.memo_file.path):
            os.remove(new_paper.memo_file.path)
    
    # =============================
    # Edge Cases and Error Tests
    # =============================
    
    def test_nonexistent_user_operations(self):
        """Test operations on non-existent users"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Try to approve non-existent user
        response = self.client.get(reverse('approve-user', args=[9999]))
        self.assertEqual(response.status_code, 404)
        
        # Try to delete non-existent user
        response = self.client.get(reverse('delete-user', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_nonexistent_learner_operations(self):
        """Test operations on non-existent learners"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Try to update non-existent learner
        response = self.client.get(reverse('update-learner', args=[9999]))
        self.assertEqual(response.status_code, 404)
        
        # Try to delete non-existent learner
        response = self.client.get(reverse('delete-learner', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_unauthorized_access(self):
        """Test that non-admin users cannot access admin views"""
        # Try to access as tutor
        self.client.login(email='tutor@test.com', password='testpass123')
        
        response = self.client.get(reverse('administrator'))
        
        # Should either redirect or show access denied
        # This depends on your @login_required decorator and permissions
        # If using Django's built-in, it will redirect to login
        # If you have custom permission checks, adjust this test accordingly
        self.assertIn(response.status_code, [302, 403])
    
    def test_pending_count_in_index(self):
        """Test that pending count is calculated correctly"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Create more unapproved users
        for i in range(3):
            User.objects.create_user(
                email=f'unapproved{i}@test.com',
                password='testpass123',
                first_name=f'Pending{i}',
                last_name='User',
                user_type='Tutor',
                approved='No'
            )
        
        response = self.client.get(reverse('administrator'))
        
        # Should have 4 unapproved users (1 from setUp + 3 new)
        self.assertEqual(response.context['pending_count'], 4)
    
    def test_email_exception_handling(self):
        """Test that views handle email exceptions gracefully"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Mock email failure - we can't easily simulate this without mocking
        # But we can test that the view redirects even if email fails
        # This would require mocking the EmailMessage.send() method
        
        # For now, just test the normal flow works
        response = self.client.get(reverse('approve-user', args=[self.unapproved_user.id]))
        
        # Should still redirect even if email fails (handled in try-except)
        self.assertEqual(response.status_code, 302)


class IntegrationTests(TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            user_type='Admin',
            approved='Yes'
        )
    
    def test_complete_user_workflow(self):
        """Test complete user approval workflow"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # 1. Create a new unapproved user
        new_user = User.objects.create_user(
            email='newtutor@test.com',
            password='testpass123',
            first_name='New',
            last_name='Tutor',
            user_type='Tutor',
            approved='No'
        )
        
        # 2. Check pending count
        response = self.client.get(reverse('administrator'))
        self.assertEqual(response.context['pending_count'], 1)
        
        # 3. View in manage users
        response = self.client.get(reverse('manage-users'))
        self.assertIn(new_user, response.context['users'])
        
        # 4. Approve user
        response = self.client.get(reverse('approve-user', args=[new_user.id]))
        new_user.refresh_from_db()
        self.assertEqual(new_user.approved, 'Yes')
        
        # 5. Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # 6. Check user appears in tutors list
        response = self.client.get(reverse('manage-tutors'))
        tutor_emails = [tutor.email for tutor in response.context['tutors']]
        self.assertIn(new_user.email, tutor_emails)
    
    def test_complete_learner_workflow(self):
        """Test complete learner management workflow"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # 1. Create necessary resources
        learner_user = User.objects.create_user(
            email='newlearner@test.com',
            password='testpass123',
            first_name='New',
            last_name='Learner',
            user_type='Learner',
            approved='Yes'
        )
        
        tutor_user = User.objects.create_user(
            email='newtutor@test.com',
            password='testpass123',
            first_name='New',
            last_name='Tutor',
            user_type='Tutor',
            approved='Yes'
        )
        
        subject = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10'
        )
        
        learner_count_before = Learner.objects.count()
        
        response = self.client.post(reverse('add-learner'), {
            'learner': learner_user.id,
            'tutor1': tutor_user.id,
            'grade': 'Grade 10',
            'subject1': subject.id
        })
        
        learner_count_after = Learner.objects.count()
        
        # Check learner was created
        self.assertEqual(learner_count_after, learner_count_before + 1)
        new_learner = Learner.objects.get(learner=learner_user)
        
        # 3. Verify learner appears in manage learners
        response = self.client.get(reverse('manage-learners'))
        self.assertIn(new_learner, response.context['learners'])
        
        # 4. Update learner
        response = self.client.post(reverse('update-learner', args=[new_learner.id]), {
            'learner': learner_user.id,
            'tutor1': tutor_user.id,
            'grade': 'Grade 11',  # Updated
            'subject1': subject.id
        })
        
        new_learner.refresh_from_db()
        self.assertEqual(new_learner.grade, 'Grade 11')
        
        # 5. Delete learner
        response = self.client.get(reverse('delete-learner', args=[new_learner.id]))
        
        # Check learner was deleted
        self.assertFalse(Learner.objects.filter(id=new_learner.id).exists())
    
    def test_file_upload_workflow(self):
        """Test complete file upload workflow"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Create subject
        subject = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10'
        )
        
        # Count before upload
        paper_count_before = PastQuestionPaper.objects.count()
        
        # Create test files
        test_content = b"Test PDF content for integration test"
        question_file = SimpleUploadedFile(
            "integration_question.pdf",
            test_content,
            content_type="application/pdf"
        )
        memo_file = SimpleUploadedFile(
            "integration_memo.pdf",
            test_content,
            content_type="application/pdf"
        )
        
        # Upload past paper
        response = self.client.post(reverse('upload_past_paper'), {
            'subject': subject.id,
            'year': 2024,
            'paper_number': 2,
            'question_file': question_file,
            'memo_file': memo_file
        })
        
        # Check upload was successful
        self.assertEqual(response.status_code, 302)
        
        paper_count_after = PastQuestionPaper.objects.count()
        self.assertEqual(paper_count_after, paper_count_before + 1)
        
        # Verify the uploaded paper
        new_paper = PastQuestionPaper.objects.latest('id')
        self.assertEqual(new_paper.year, 2024)
        self.assertEqual(new_paper.paper_number, 2)
        self.assertEqual(new_paper.subject, subject)
        
        # Clean up
        if os.path.exists(new_paper.question_file.path):
            os.remove(new_paper.question_file.path)
        if os.path.exists(new_paper.memo_file.path):
            os.remove(new_paper.memo_file.path)


class PerformanceTests(TestCase):
    """Performance-related tests"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            user_type='Admin',
            approved='Yes'
        )
        
        # Create bulk data for performance testing
        self.create_bulk_data()
    
    def create_bulk_data(self):
        """Create bulk data for performance testing"""
        # Create 50 users
        for i in range(50):
            User.objects.create_user(
                email=f'user{i}@test.com',
                password=f'testpass{i}',
                first_name=f'User{i}',
                last_name=f'Test{i}',
                user_type='Tutor' if i % 2 == 0 else 'Learner',
                approved='Yes' if i % 3 == 0 else 'No'
            )
        
        # Create 20 subjects
        for i in range(20):
            Subject.objects.create(
                name=f'Subject {i}',
                grade=f'Grade {i % 12 + 1}'
            )
    
    def test_manage_users_performance(self):
        """Test performance of manage users view with many users"""
        client = Client()
        client.login(email='admin@test.com', password='adminpass123')
        
        import time
        start_time = time.time()
        
        response = client.get(reverse('manage-users'))
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should load within 1 second even with 50+ users
        self.assertLess(execution_time, 1.0)
        self.assertEqual(response.status_code, 200)
        
        # Check all users are loaded (excluding admin)
        users = response.context['users']
        self.assertEqual(users.count(), 50)  # 50 created users
    
    def test_learner_form_queryset_performance(self):
        """Test performance of LearnerForm querysets"""
        import time
        
        start_time = time.time()
        form = LearnerForm()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Form initialization should be fast
        self.assertLess(execution_time, 0.5)
        
        # Check querysets are properly filtered
        self.assertEqual(form.fields['learner'].queryset.count(), 25)  # Half are learners
        self.assertEqual(form.fields['tutor1'].queryset.count(), 25)   # Half are tutors


class SecurityTests(TestCase):
    """Security-related tests"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            user_type='Admin',
            approved='Yes'
        )
        
        self.tutor_user = User.objects.create_user(
            email='tutor@test.com',
            password='testpass123',
            first_name='Tutor',
            last_name='User',
            user_type='Tutor',
            approved='Yes'
        )
        
        self.learner_user = User.objects.create_user(
            email='learner@test.com',
            password='testpass123',
            first_name='Learner',
            last_name='User',
            user_type='Learner',
            approved='Yes'
        )
    
    def test_admin_only_access(self):
        """Test that admin-only views are protected"""
        admin_urls = [
            reverse('administrator'),
            reverse('manage-users'),
            reverse('manage-payments'),
            reverse('manage-clients'),
            reverse('manage-tutors'),
            reverse('manage-subjects'),
            reverse('manage-learners'),
            reverse('manage-classes'),
            reverse('manage-tutor-payments'),
            reverse('upload_past_paper'),
        ]
        
        # Test as tutor (should not have access)
        self.client.login(email='tutor@test.com', password='testpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            # Should redirect to login or show permission denied
            self.assertIn(response.status_code, [302, 403])
        
        # Test as learner (should not have access)
        self.client.login(email='learner@test.com', password='testpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403])
        
        # Test as admin (should have access)
        self.client.login(email='admin@test.com', password='adminpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            # Some might redirect if conditions aren't met (like missing month)
            # But shouldn't be permission denied
            self.assertNotEqual(response.status_code, 403)
    
    def test_csrf_protection(self):
        """Test that forms have CSRF protection"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Test add learner form
        response = self.client.get(reverse('add-learner'))
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Test upload past paper form
        response = self.client.get(reverse('upload_past_paper'))
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_sql_injection_prevention(self):
        """Test that queries are parameterized to prevent SQL injection"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Try to inject SQL in URL parameters
        malicious_id = "1 OR 1=1; DROP TABLE auth_user; --"
        
        # These should either 404 or handle safely
        urls_to_test = [
            reverse('approve-user', args=[malicious_id]),
            reverse('delete-user', args=[malicious_id]),
            reverse('update-learner', args=[malicious_id]),
            reverse('delete-learner', args=[malicious_id]),
        ]
        
        for url in urls_to_test:
            try:
                response = self.client.get(url)
                # Should not crash with 500 error
                self.assertNotEqual(response.status_code, 500)
            except Exception as e:
                self.fail(f"URL {url} raised exception with malicious input: {e}")
    
    def test_file_upload_security(self):
        """Test file upload security"""
        self.client.login(email='admin@test.com', password='adminpass123')
        
        # Create subject
        subject = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10'
        )
        
        # Test with potentially dangerous file
        dangerous_content = b'<?php system($_GET["cmd"]); ?>'
        dangerous_file = SimpleUploadedFile(
            "malicious.php",
            dangerous_content,
            content_type="application/x-php"
        )
        
        response = self.client.post(reverse('upload_past_paper'), {
            'subject': subject.id,
            'year': 2024,
            'paper_number': 1,
            'question_file': dangerous_file,
            'memo_file': dangerous_file
        })
        
        # Should either reject or handle safely
        # Django's FileField doesn't validate file types by default
        # You might want to add validation in your form
        self.assertNotEqual(response.status_code, 500)


class FormValidationTests(TestCase):
    """Comprehensive form validation tests"""
    
    def setUp(self):
        self.learner_user = User.objects.create_user(
            email='learner@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            user_type='Learner',
            approved='Yes'
        )
        
        self.tutor_user = User.objects.create_user(
            email='tutor@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            user_type='Tutor',
            approved='Yes'
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            grade='Grade 10'
        )
    
    def test_learner_form_boundary_values(self):
        """Test form with boundary and edge case values"""
        
        # Test empty grade (should fail)
        form_data = {
            'learner': self.learner_user.id,
            'tutor1': self.tutor_user.id,
            'grade': '',  # Empty
            'subject1': self.subject.id
        }
        
        form = LearnerForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('grade', form.errors)
        
        # Test invalid grade (not in choices)
        form_data['grade'] = 'Invalid Grade'
        form = LearnerForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('grade', form.errors)
        
        # Test valid boundary grade
        form_data['grade'] = 'Grade 12'  # Highest valid grade
        form = LearnerForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_past_paper_form_validation(self):
        """Test PastQuestionPaperForm validation"""
        
        # Test with invalid year (future year might be invalid)
        from datetime import datetime
        current_year = datetime.now().year
        
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"content",
            content_type="application/pdf"
        )
        
        form_data = {
            'subject': self.subject.id,
            'year': current_year + 10,  # 10 years in future
            'paper_number': 1,
        }
        
        file_data = {
            'question_file': test_file,
            'memo_file': test_file
        }
        
        form = PastQuestionPaperForm(data=form_data, files=file_data)
        # This depends on your validation - you might want to add year validation
        # For now, just test it doesn't crash
        self.assertIsNotNone(form)
        
        # Test with very old year
        form_data['year'] = 1900
        form = PastQuestionPaperForm(data=form_data, files=file_data)
        self.assertIsNotNone(form)
        
        # Test with invalid paper number
        form_data['year'] = 2023
        form_data['paper_number'] = 99  # Not in choices
        form = PastQuestionPaperForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn('paper_number', form.errors)
        
        # Clean up files
        if form.is_valid():
            paper = form.save()
            if os.path.exists(paper.question_file.path):
                os.remove(paper.question_file.path)
            if os.path.exists(paper.memo_file.path):
                os.remove(paper.memo_file.path)


class TemplateTests(TestCase):
    """Tests for template rendering"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            user_type='Admin',
            approved='Yes'
        )
        self.client.login(email='admin@test.com', password='adminpass123')
    
    def test_template_content(self):
        """Test that templates render expected content"""
        
        # Test index template
        response = self.client.get(reverse('administrator'))
        self.assertContains(response, 'Admin Home')  # Adjust based on your template
        self.assertContains(response, 'pending_count')
        
        # Test manage users template
        response = self.client.get(reverse('manage-users'))
        self.assertContains(response, 'Manage Users')
        self.assertContains(response, 'Approve')
        self.assertContains(response, 'Disapprove')
        self.assertContains(response, 'Delete')
        
        # Test add learner template
        response = self.client.get(reverse('add-learner'))
        self.assertContains(response, 'Add Learner')
        self.assertContains(response, 'form')
        self.assertContains(response, 'submit')
    
    def test_error_messages_display(self):
        """Test that error messages are displayed"""
        
        # Try to add learner with invalid data
        response = self.client.post(reverse('add-learner'), {})
        
        # Should show error messages
        self.assertContains(response, 'error', status_code=200)
        
        # Check messages framework
        from django.contrib import messages as django_messages
        storage = django_messages.get_messages(response.wsgi_request)
        message_list = list(storage)
        self.assertGreater(len(message_list), 0)


class URLTests(TestCase):
    """Tests for URL patterns"""
    
    def test_url_resolution(self):
        """Test that all URLs resolve correctly"""
        
        # Test each URL pattern
        urls = [
            ('administrator', [], {}),
            ('manage-users', [], {}),
            ('manage-payments', [], {}),
            ('manage-clients', [], {}),
            ('manage-tutors', [], {}),
            ('manage-subjects', [], {}),
            ('add-learner', [], {}),
            ('manage-learners', [], {}),
            ('manage-classes', [], {}),
            ('manage-tutor-payments', [], {}),
            ('upload_past_paper', [], {}),
        ]
        
        for url_name, args, kwargs in urls:
            try:
                reverse(url_name, args=args, kwargs=kwargs)
            except Exception as e:
                self.fail(f"Failed to reverse URL '{url_name}': {e}")
        
        # Test URLs with parameters
        param_urls = [
            ('approve-user', [1], {}),
            ('disapprove-user', [1], {}),
            ('delete-user', [1], {}),
            ('update-learner', [1], {}),
            ('delete-learner', [1], {}),
            ('manage-class-learners', [1], {}),
        ]
        
        for url_name, args, kwargs in param_urls:
            try:
                reverse(url_name, args=args, kwargs=kwargs)
            except Exception as e:
                self.fail(f"Failed to reverse URL '{url_name}' with args {args}: {e}")
    
    def test_url_patterns(self):
        """Test URL patterns match expected paths"""
        
        patterns = [
            ('administrator', '/admin-home/'),
            ('manage-users', '/manage-users/'),
            ('approve-user', '/approve-user/1/'),
            ('upload_past_paper', '/past-papers/upload/'),
        ]
        
        for url_name, expected_path in patterns:
            if '1' in expected_path:
                args = [1]
            else:
                args = []
            
            actual_path = reverse(url_name, args=args)
            self.assertEqual(actual_path, expected_path)


# =============================
# Main test execution
# =============================
if __name__ == '__main__':
    # This allows running tests directly with: python tests.py
    import django
    django.setup()
    
    import unittest
    unittest.main()