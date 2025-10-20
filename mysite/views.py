from rest_framework.views import APIView
from rest_framework.response import Response

# Used only for global pages (such as homepage)

class HomepageView(APIView):
    def get(self, request):
        return Response({"message": "Bună ziua!"})