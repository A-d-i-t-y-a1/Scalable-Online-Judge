from django.contrib import admin
from .models import Problems,Solution,TestCases
# Register your models here.
admin.site.register(Problems)
admin.site.register(Solution)
admin.site.register(TestCases)