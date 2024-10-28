# from celery import Celery
# from celery.schedules import crontab
#
# app = Celery('LMSV2',
#              broker='redis://127.0.0.1:6379/0',
#              backend='redis://127.0.0.1:6379/0',
#              include=['tasks'])
#
# app.conf.beat_schedule = {
#     'check-expiry-dates-every-day': {
#         'task': 'tasks.write_to_file',
#         'schedule': crontab(minute='45', hour='19'),  # Execute daily at 5:55 PM
#     },
# }
#
# if __name__ == '__main__':
#     app.start()

from celery import Celery
from celery.schedules import crontab

app = Celery('HSM',
             broker='redis://127.0.0.1:6379/0',
             backend='redis://127.0.0.1:6379/0',
             include=['tasks'])

app.conf.beat_schedule = {
    'run-test-task-every-minute': {
        'task': 'tasks.check_pending_reqs',
        'schedule': crontab('*/1'),  # Execute every minute
    },
}