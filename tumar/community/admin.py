from django.contrib import admin
from django.db.models import Q
from django import forms

from .models import Post, Comment, PostImage, CommentImage

# Register your models here.


class InLineComment(admin.TabularInline):
    model = Comment
    extra = 1


class InLinePostImage(admin.TabularInline):
    model = PostImage
    extra = 1


class InLineCommentImage(admin.TabularInline):
    model = CommentImage
    extra = 1


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        # Excluding comment itself and its replies from "select" widget of reply_object
        #  field
        self.fields["reply_object"].queryset = Comment.objects.exclude(
            Q(id=self.instance.id)
            | Q(id__in=self.instance.replies.values_list("id", flat=True))
        )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [InLinePostImage, InLineComment]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    inlines = [InLineCommentImage]
    form = CommentForm
