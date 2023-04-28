from django.contrib import admin
from .models import Poll, Token

# Register your models
admin.site.register(Poll)
admin.site.register(Token)