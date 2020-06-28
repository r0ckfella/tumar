from ..celery import app
from ..notify.models import Notification
from .models import Comment, CommentVote, PostVote, Post


@app.task(
    name="send_push_notification.new_comment_on_post",
    queue="community_push_notifications",
)
def task_send_push_notification_new_comment_on_post(comment_pk):
    comment = Comment.objects.get(pk=comment_pk)

    ntfcn = Notification.objects.create(
        receiver=comment.post.user,
        content=('На ваш пост "{}..." ответили комментарием "{}..."!').format(
            comment.post.title[:10], comment.content[:10]
        ),
    )
    ntfcn.send()


@app.task(
    name="send_push_notification.new_reply_comment",
    queue="community_push_notifications",
)
def task_send_push_notification_new_reply_comment(comment_pk):
    comment = Comment.objects.get(pk=comment_pk)

    ntfcn = Notification.objects.create(
        receiver=comment.reply_object.user,
        content=('На ваш комментарий "{}..." ответили комментарием "{}..."!').format(
            comment.reply_object.content[:10], comment.content[:10]
        ),
    )
    ntfcn.send()


@app.task(
    name="send_push_notification.new_vote_on_comment",
    queue="community_push_notifications",
)
def task_send_push_notification_new_vote_on_comment(comment_vote_pk):
    comment_vote = CommentVote.objects.get(pk=comment_vote_pk)

    ntfcn = Notification.objects.create(
        receiver=comment_vote.comment.user,
        content=('Ваш комментарий "{}..." кому-то {}.').format(
            comment_vote.comment.content[:10],
            "понравился" if comment_vote.type == "U" else "не понравился",
        ),
    )
    ntfcn.send()


@app.task(
    name="send_push_notification.new_vote_on_post",
    queue="community_push_notifications",
)
def task_send_push_notification_new_vote_on_post(post_vote_pk):
    post_vote = PostVote.objects.get(pk=post_vote_pk)

    ntfcn = Notification.objects.create(
        receiver=post_vote.post.user,
        content=('Ваш пост "{}..." кому-то {}.').format(
            post_vote.post.content[:10],
            "понравился" if post_vote.type == "U" else "не понравился",
        ),
    )
    ntfcn.send()


@app.task(
    name="send_push_notifications.new_post", queue="community_push_notifications",
)
def task_send_push_notifications_new_post(post_pk_list):
    for pk in post_pk_list:
        post = Post.objects.get(pk=pk)

        ntfcn = Notification.objects.create(
            receiver=post.user,
            content=('Новый пост "{}..." был только что опубликован.').format(
                post.content[:10],
            ),
        )
        ntfcn.send(extra={"post_pk": pk})
