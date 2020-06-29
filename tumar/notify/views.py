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


class NotificationMarkAsReadView(APIView):
    def get(self, request, pk):
        ntfcn = Notification.objects.get(pk=pk)
        ntfcn.mark_as_read()

        return Response(
            {
                "success": "True",
                "unread_count": Notification.objects.filter(
                    receiver=request.user
                ).unread_count(),
            },
            status=status.HTTP_200_OK,
        )
