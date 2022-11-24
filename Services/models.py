from django.db import models


class QueuePushNotification(models.Model):
    priority = models.PositiveSmallIntegerField(default=10)  # priority from 1 to 10
    timestamp = models.DateTimeField()  # after this ts you can send notification
    status = models.SmallIntegerField()  # what if our push-send server will fall down?
    # tokens_type = models.SmallIntegerField()
    tokens = models.TextField()  # always as array of tokens
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.TextField()

    class Meta:
        ordering = ['priority', 'timestamp']
