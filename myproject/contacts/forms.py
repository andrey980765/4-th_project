# contacts/forms.py
from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    SAVE_CHOICES = [
        ('db', 'Сохранить в базу данных (SQLite)'),
        ('json', 'Сохранить в JSON файл'),
        ('xml', 'Сохранить в XML файл'),
    ]
    save_to = forms.ChoiceField(choices=SAVE_CHOICES, widget=forms.RadioSelect, initial='db')

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'notes', 'save_to']
