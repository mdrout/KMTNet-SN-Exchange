from django.contrib import admin

# Register your models here.
from .models import Field,Classification,Comment

admin.site.register(Field)
admin.site.register(Classification)
admin.site.register(Comment)
