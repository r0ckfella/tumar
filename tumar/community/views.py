from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    Post,
    Comment,
    CommentImage,
    PostImage,
    PostVote,
    CommentVote,
)
from .serializers import (
    CommentSerializer,
    PostCategorySerializer,
    PostSerializer,
    PostCreateUpdateSerializer,
)

# Create your views here.


class PostCategoryListView(APIView):
    def get(self, request):
        all_categories = Category.objects.all().order_by("id")
        serializer = PostCategorySerializer(all_categories, many=True)

        return Response(serializer.data)


class PostReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves companies
    """

    queryset = Post.objects.all().order_by("created_at")
    model = Post
    serializer_class = PostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("categories",)

    # def get_serializer_context(self):
    #     context = super(PostReadOnlyViewSet, self).get_serializer_context()
    #     context.update({"user": self.request.user})
    #     return context


class MyPostsView(APIView):
    def get(self, request):
        my_posts = Post.objects.filter(user=request.user).order_by("created_at")
        serializer = PostSerializer(my_posts, many=True, context={"request": request})

        return Response(serializer.data)


class PostCreateView(APIView):
    def post(self, request):
        # Prohibit if a user assigned Лучшее category to a post
        if not request.user.is_superuser and "categories" in request.data:
            categories_data = request.data.get("categories")
            hot_category_id = Category.objects.get(name="Лучшее").id
            for category_id in categories_data:
                if int(category_id) == hot_category_id:
                    return Response(
                        {"fail": "Only admins can assign Лучшее category"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

        serializer = PostCreateUpdateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostUpdateDestroyView(APIView):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, id=post_pk)

        serializer = PostSerializer(post, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, post_pk):
        # Prohibit if a user assigned Лучшее category to a post
        if not request.user.is_superuser and "categories" in request.data:
            categories_data = request.data.get("categories")
            hot_category_id = Category.objects.get(name="Лучшее").id
            for category_id in categories_data:
                if int(category_id) == hot_category_id:
                    return Response(
                        {"fail": "Only admins can assign Лучшее category"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

        post = None
        if request.user.is_superuser:
            post = get_object_or_404(Post, id=post_pk)
        else:
            post = get_object_or_404(Post, user=request.user, id=post_pk)

        serializer = PostCreateUpdateSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_pk):
        post = None
        if request.user.is_superuser:
            post = get_object_or_404(Post, id=post_pk)
        else:
            post = get_object_or_404(Post, user=request.user, id=post_pk)
        post.delete()
        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)


class PostImageDestroyView(APIView):
    def delete(self, request, img_pk):
        img = None
        if request.user.is_superuser:
            img = get_object_or_404(PostImage, id=img_pk)
        else:
            img = get_object_or_404(PostImage, post__user=request.user, id=img_pk)
        img.delete()
        return Response({"deleted": img_pk}, status=status.HTTP_204_NO_CONTENT)


class PostVoteView(APIView):
    def get(self, request, post_pk, vote_type):
        post = get_object_or_404(Post, pk=post_pk)
        vote, created = PostVote.objects.get_or_create(post=post, user=request.user)

        if created:
            vote.type = vote_type
            vote.save()
        else:
            if vote.type == vote_type:
                vote.delete()
            else:
                vote.type = vote_type
                vote.save()

        return Response({"success": True}, status=status.HTTP_200_OK)


class CommentListView(APIView):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, id=post_pk)

        serializer = CommentSerializer(
            post.comments, many=True, context={"user": self.request.user}
        )

        return Response(serializer.data)


class CommentCreateView(APIView):
    def post(self, request):
        serializer = CommentSerializer(
            data=request.data, context={"user": request.user}
        )

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
        comment = None
        if request.user.is_superuser:
            comment = get_object_or_404(Comment, id=comment_pk)
        else:
            comment = get_object_or_404(Comment, user=request.user, id=comment_pk)

        serializer = CommentSerializer(comment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_pk):
        comment = None
        if request.user.is_superuser:
            comment = get_object_or_404(Comment, id=comment_pk)
        else:
            comment = get_object_or_404(Comment, user=request.user, id=comment_pk)
        comment.delete()
        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)


class CommentImageDestroyView(APIView):
    def delete(self, request, img_pk):
        img = None
        if request.user.is_superuser:
            img = get_object_or_404(CommentImage, id=img_pk)
        else:
            img = get_object_or_404(CommentImage, comment__user=request.user, id=img_pk)
        img.delete()
        return Response({"deleted": img_pk}, status=status.HTTP_204_NO_CONTENT)


class CommentVoteView(APIView):
    def get(self, request, comment_pk, vote_type):
        comment = get_object_or_404(Comment, pk=comment_pk)
        vote, created = CommentVote.objects.get_or_create(
            comment=comment, user=request.user
        )

        if created:
            vote.type = vote_type
            vote.save()
        else:
            if vote.type == vote_type:
                vote.delete()
            else:
                vote.type = vote_type
                vote.save()

        return Response({"success": True}, status=status.HTTP_200_OK)
