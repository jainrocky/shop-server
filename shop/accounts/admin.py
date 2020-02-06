from django.contrib import admin
from django.contrib.auth.models import Group
from .models import UserProfile, UserHistory, User

admin.site.unregister(Group)

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserHistory)
