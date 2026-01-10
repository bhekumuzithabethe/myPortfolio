from datetime import datetime
from .models import Month
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
import os

# =============================
# Task: Monthly Data Creation
# =============================
def monthly_tasks():
    """
    This function ensures that a new Month instance is created 
    once per calendar month, based on the current date.
    """
    try:
        now = datetime.now()
        month_name = now.strftime("%B %Y")  # e.g., "July 2025"

        # Only create a new Month instance if it doesn't already exist
        Month.objects.get_or_create(current_month=month_name)

    except Exception as e:
        # Log scheduler error
        print(f"Scheduler error: {e}")

# =============================
# Scheduler Initialization
# =============================
def start():
    """
    Initializes the background scheduler with APScheduler.
    Prevents the scheduler from running multiple times during Django's autoreload.
    """
    if os.environ.get('RUN_MAIN') != 'true':
        return  # Prevent duplicate scheduler threads caused by Django runserver

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")  # Use Django's DB as job store

    # Schedule the job to run on the 1st day of every month at 00:00
    scheduler.add_job(
        monthly_tasks,
        trigger=CronTrigger(day=1, hour=0, minute=0),
        id="monthly_model_creation",  # Unique job ID
        replace_existing=True,        # Replaces the job if it already exists
    )
    scheduler.start()