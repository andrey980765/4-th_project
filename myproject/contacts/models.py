from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Можно добавить индекс/unique_together, но мы будем проверять в форме.
        indexes = [
            models.Index(fields=['name', 'email']),
        ]

    def __str__(self):
        return f"{self.name} <{self.email}>"
# Create your models here.
