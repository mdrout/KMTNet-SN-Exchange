from django.contrib import admin

# Register your models here.
from .models import Field,Classification

admin.site.register(Field)
admin.site.register(Classification)