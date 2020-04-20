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
        read_only_fields = ("name",)


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
    my_upvote = serializers.SerializerMethodField()
    my_downvote = serializers.SerializerMethodField()

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
            "my_upvote",
            "my_downvote",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "votes_count",
            "is_active",
            "user",
            "replies",
        )
        extra_kwargs = {
            "post": {"write_only": True},
        }

    def get_my_upvote(self, obj):
        return obj.votes.filter(type="U", user=self.context["user"]).exists()

    def get_my_downvote(self, obj):
        return obj.votes.filter(type="D", user=self.context["user"]).exists()

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
    images = PostImageSerializer(required=False, allow_null=True, many=True)
    user = UserPreviewSerializer(required=False, allow_null=True)
    my_upvote = serializers.SerializerMethodField()
    my_downvote = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "comments_count",
            "votes_count",
            "is_active",
            "user",
            "images",
            "categories",
            "my_upvote",
            "my_downvote",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "votes_count",
            "comments_count",
            "is_active",
            "user",
            "categories",
        )

    def get_my_upvote(self, obj):
        return obj.votes.filter(type="U", user=self.context["request"].user).exists()

    def get_my_downvote(self, obj):
        return obj.votes.filter(type="D", user=self.context["request"].user).exists()


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(required=False, allow_null=True, many=True)
    user = UserPreviewSerializer(required=False, allow_null=True)
    categories = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=Category.objects.all(),
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "comments_count",
            "votes_count",
            "is_active",
            "user",
            "images",
            "categories",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "votes_count",
            "comments_count",
            "is_active",
            "user",
        )

    def create(self, validated_data):
        images_data = None
        categories = None
        if "images" in validated_data:
            images_data = validated_data.pop("images")
        if "categories" in validated_data:
            categories = validated_data.pop("categories")

        # maybe categories = validated_data.pop("categories", [])

        post = Post.objects.create(**validated_data)

        if images_data:
            for image_data in images_data:
                post.images.create(**image_data)
        if categories:
            for category in categories:
                # if a category needs to be created instantly, it can be done here
                post.categories.add(category)

        return post

    def update(self, instance, validated_data):
        images_data = None
        categories = None
        if "images" in validated_data:
            images_data = validated_data.pop("images")
        if "categories" in validated_data:
            categories = validated_data.pop("categories")

        if "id" in validated_data:
            validated_data.pop("id")
        instance = super(PostCreateUpdateSerializer, self).update(
            instance, validated_data
        )

        if images_data:
            for image_data in images_data:
                if "id" not in image_data:
                    instance.images.create(**image_data)
        if categories:
            for category in categories:
                # if a category needs to be created instantly, it can be done here
                # category = Category.objects.get(pk=category_id)
                instance.categories.clear()
                instance.categories.add(category)

        return instance


class SinglePostSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("comments",)
