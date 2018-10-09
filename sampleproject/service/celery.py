from __future__ import absolute_import, unicode_literals
from celery import Celery


app = Celery('service',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/1',
             include=['service.tasks'])


# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)


if __name__ == '__main__':
    app.start()
