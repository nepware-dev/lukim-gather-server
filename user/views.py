from django.http import HttpResponse
from oauth2_provider.views.generic import ProtectedResourceView


class UserInfoView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        user = request.user
        return HttpResponse(
            {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )
