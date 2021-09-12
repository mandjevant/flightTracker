from apscheduler.events import EVENT_JOB_ERROR
from app import scheduler


def job_error(event):
    """
    Error handling for scheduled jobs
    """
    with scheduler.app.app_context():
        print(event)
        pass


scheduler.add_listener(job_error, EVENT_JOB_ERROR)
