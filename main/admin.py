from django.contrib import admin
from main.models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(RequestCount)