from django.db import models

class Template(models.Model):
    template_name = models.CharField(max_length=200)
    template_text = models.TextField()
