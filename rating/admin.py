from django.contrib import admin
from .models import Professor, Module, ModuleInstance


admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(ModuleInstance)
