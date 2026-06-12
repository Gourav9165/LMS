from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_librarian = models.BooleanField(default=False)
    is_member = models.BooleanField(default=True)
    library_card_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({'Librarian' if self.is_librarian else 'Member'})"