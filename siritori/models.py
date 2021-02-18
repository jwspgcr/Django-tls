from django.db import models

class Session(models.Model):
    key = models.CharField(max_length=50,primary_key=True)
    lastWord = models.CharField(max_length=50)

    def __str__(self):
        return self.key
