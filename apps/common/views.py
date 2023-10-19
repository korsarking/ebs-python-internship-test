from rest_framework.generics import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class HealthView(views.APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response({"live": True})
