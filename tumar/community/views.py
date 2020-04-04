from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Post, Comment, CommentImage
from .serializers import CommentSerializer, PostCategorySerializer, PostSerializer

# Create your views here.


class PostCategoryListView(APIView):
    def get(self, request):
        all_categories = Category.objects.all().order_by("id")
        serializer = PostCategorySerializer(all_categories, many=True)

        return Response(serializer.data)


class CommentListView(APIView):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, id=post_pk)

        serializer = CommentSerializer(post.comments, many=True)

        return Response(serializer.data)


class CommentCreateView(APIView):
    def post(self, request):
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentUpdateDestroyView(APIView):
    def patch(self, request, comment_pk):
        if "reply_object" in request.data:
            return Response(
                {"error": "Cannot change reply object"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = get_object_or_404(Comment, id=comment_pk)

        serializer = CommentSerializer(comment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_pk):
        comment = get_object_or_404(Comment, id=comment_pk)
        comment.delete()
        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)


class DestroyCommentImage(APIView):
    def delete(self, request, img_pk):
        img = get_object_or_404(CommentImage, id=img_pk)
        img.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves companies
    """

    queryset = Post.objects.all().order_by("created_at")
    model = Post
    serializer_class = PostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("categories",)

    # def get_serializer_class(self):
    #     serializers_class_map = {
    #         "retrieve": SinglePostSerializer,
    #         "list": PostSerializer,
    #     }

    #     return serializers_class_map.get(self.action)
