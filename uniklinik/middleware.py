from django.shortcuts import render
from django.contrib.sessions.middleware import SessionMiddleware


class LogoutSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        request.session.flush()


class RejectAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        print(f"hahaha: {request.user.id}")
        if request.user.id:
            if request.user.profile.is_admin in [False, None, ""]:
                print(f"love: {request.user.is_superuser}")
                if request.user.is_superuser in [False, None, ""]:
                    return render(request, "reject_page.html", {})
        # Code to be executed for each request/response after
        # the view is called.
        return response
