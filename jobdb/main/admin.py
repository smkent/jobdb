from django.contrib import admin

from .models import Application, Company, Posting, User

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Posting)
admin.site.register(Application)
