from rest_framework import serializers

from ..users.serializers import UserPreviewSerializer
from .models import Category, Comment, Post, PostImage, CommentImage


class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = (
            "id",
            "image",
        )


class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = (
            "id",
            "image",
        )


class CommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(required=False, allow_null=True, many=True)
    user = UserPreviewSerializer(required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "images",
            "created_at",
            "updated_at",
            "votes_count",
            "is_active",
            "user",
            "reply_object",
            "replies",
            "post",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "votes_count",
            "is_active",
            "replies",
            "user",
        )
        extra_kwargs = {
            "post": {"write_only": True},
        }

    def create(self, validated_data):
        images_data = None
        if "images" in validated_data:
            images_data = validated_data.pop("images")

        comment = Comment.objects.create(**validated_data)

        if images_data:
            for image_data in images_data:
                comment.images.create(**image_data)
        return comment

    def update(self, instance, validated_data):
        images_data = None
        if "images" in validated_data:
            images_data = validated_data.pop("images")

        if "id" in validated_data:
            validated_data.pop("id")  # remove id, since we already have instance obj
        instance = super(CommentSerializer, self).update(instance, validated_data)

        if images_data:
            for image_data in images_data:
                if "id" not in image_data:
                    instance.images.create(**image_data)

        return instance


class PostSerializer(serializers.ModelSerializer):
    categories = PostCategorySerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True)
    user = UserPreviewSerializer()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "updated_at",
            "created_at",
            "comments_count",
            "votes_count",
            "is_active",
            "user",
            "images",
            "categories",
        )


class SinglePostSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("comments",)
