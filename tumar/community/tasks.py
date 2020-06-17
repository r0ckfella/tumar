from ..celery import app
from ..notify.models import Notification


@app.task(
    name="send_push_notification.new_comment_on_post",
    queue="community_push_notifications",
)
def task_send_push_notification_new_comment_on_post(comment):
    ntfcn = Notification.objects.create(
        receiver=comment.post.user,
        content=('На ваш пост "{}..." ответили комментарием "{}..."!').format(
            comment.post.title[:10], comment.content[:10]
        ),
    )
    # ntfcn.send()


@app.task(
    name="send_push_notification.new_vote_on_comment",
    queue="community_push_notifications",
)
def task_send_push_notification_new_vote_on_comment(comment_vote):
    ntfcn = Notification.objects.create(
        receiver=comment_vote.comment.user,
        content=('Ваш комментарий "{}..." кому-то {}.').format(
            comment_vote.comment.content[:10],
            "понравился" if comment_vote.type == "U" else "не понравился",
        ),
    )
    # ntfcn.send()


@app.task(
    name="send_push_notifications.new_post", queue="community_push_notifications",
)
def task_send_push_notifications_new_post(post):
    pass
