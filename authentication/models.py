from django.db import models
from django.contrib.auth.models import User
import random

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=4, blank=True)

    def generate_verification_code(self):
        code = ''.join(random.choices('0123456789', k=4))
        self.verification_code = code
        self.save()
