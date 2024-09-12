from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse

def Admin_required():
    def is_admin(user):
        if user.is_authenticated and (user.is_superuser or user.is_staff):
            return True
        return True
    return user_passes_test(is_admin)