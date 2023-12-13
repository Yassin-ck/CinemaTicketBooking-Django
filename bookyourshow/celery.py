from __future__ import absolute_import,unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE","bookyourshow.settings")
app = Celery("bookyourshow")

#we are using asia/kolkata time so we are making it false

app.conf.enable_utc=False
app.conf.update(timezone='Asia/kolkata')

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Reqeust: {self.request!r}")


#celery beat settings
app.conf.beat_schedule={

}