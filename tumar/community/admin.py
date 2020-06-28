from django import forms
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from ..celery import app
from .models import Post, Comment, PostImage, CommentImage, PostLink

# Register your models here.


class InLineComment(admin.TabularInline):
    model = Comment
    extra = 1


class InLinePostImage(admin.TabularInline):
    model = PostImage
    extra = 1


class InLinePostLink(admin.TabularInline):
    model = PostLink
    extra = 1
    max_num = 2


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
    inlines = [InLinePostImage, InLineComment, InLinePostLink]
    actions = [
        "send_push_notifications",
    ]

    @method_decorator(staff_member_required)
    def send_push_notifications(self, request, queryset):
        post_pks = queryset.values_list("id", flat=True)

        ntfcn_task = app.signature(
            "send_push_notifications.new_post",
            kwargs={"post_pk_list": list(post_pks)},
            queue="community_push_notifications",
            priority=5,
        )

        ntfcn_task.delay()

        self.message_user(request, _("Push notifications were just sent to all users."))
        return HttpResponseRedirect("../")

    send_push_notifications.short_description = _(
        "Send push notifications to all users"
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    inlines = [InLineCommentImage]
    form = CommentForm
