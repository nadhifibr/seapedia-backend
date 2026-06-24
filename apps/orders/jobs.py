import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.conf import settings
from .services import process_overdue_orders

logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Run every 5 minutes
    scheduler.add_job(
        process_overdue_orders,
        trigger="interval",
        minutes=5,
        id="process_overdue_orders_job",
        replace_existing=True,
        max_instances=1
    )

    register_events(scheduler)
    scheduler.start()
    logger.info("Overdue Scheduler started...")
