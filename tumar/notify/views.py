from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer

# Create your views here.


class NotificationListView(APIView):
    def get(self, request):
        user_notifications = Notification.objects.filter(
            receiver=request.user, read=False
        ).order_by("-created_at")
        serializer = NotificationSerializer(user_notifications, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
