from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden

class AdminMiddleware():
    def __init__(self, get_response):
        self.get_response= get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                return HttpResponseForbidden("You don't have the permission to access this page")
            
        response= self.get_response(request)
        return response
    
class AdminAccessMiddleware(AdminMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)