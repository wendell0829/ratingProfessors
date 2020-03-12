from django.contrib import admin
from .models import User, Professor, Module, ModuleInstance, RatingRecord


# admin.site.register(User)
admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(ModuleInstance)
admin.site.register(RatingRecord)