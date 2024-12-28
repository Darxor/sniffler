from django.db import models


class ScanResult(models.Model):
    id = models.AutoField(primary_key=True)
    path = models.CharField(max_length=255)
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.path
