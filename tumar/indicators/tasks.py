import datetime
import logging

from django.db.models import Q
from celery import shared_task

from ..celery import app
from ..notify.models import Notification
from .choices import FAILED, FINISHED, WAITING, FREE_EXPIRED
from .models import ImageryRequest

logger = logging.getLogger(__name__)


def run_image_processing_task(imagery_request, egistic_cadastre_pk, immediate=True):
    target_dates = [
        imagery_request.requested_date,
    ]

    result = app.signature(
        "process_cadastres",
        kwargs={
            "param_values": dict(param="id", values=[egistic_cadastre_pk]),
            "target_dates": target_dates,
            "days_range": 14,
        },
        queue="process_cadastres",
        priority=5,
    )

    result_handler_task_name = "tumar_handler_process_cadastres"
    handler_task = app.signature(
        result_handler_task_name,
        kwargs={"imageryrequest_id": imagery_request.id},
        queue=result_handler_task_name,
    )

    if immediate:
        (
            result.on_error(log_error.s(imageryrequest_id=imagery_request.id))
            | handler_task
        ).delay()
    else:
        (
            result.on_error(log_error.s(imageryrequest_id=imagery_request.id))
            | handler_task
        ).apply_async(eta=imagery_request.requested_date)


@app.task(
    name="tumar_error_handler_process_cadastres",
    queue="tumar_handler_process_cadastres",
)
def log_error(request, exc, traceback, imageryrequest_id):
    try:
        imagery_request = ImageryRequest.objects.get(pk=imageryrequest_id)
    except ImageryRequest.DoesNotExist:
        logger.critical(
            "This shouldn't have happened. Imagery Request {} does not exist.".format(
                imageryrequest_id
            )
        )

    logger.critical(
        "Imagery Request #{} FAILED!\n\n-- request.id:{0} exc:{1} traceback:{2}".format(
            imagery_request.pk, request.id, exc, traceback,
        )
    )
    imagery_request.status = FAILED
    imagery_request.save()


@shared_task(
    bind=False,
    ignore_result=True,
    name="tumar_handler_process_cadastres",
    queue="tumar_handler_process_cadastres",
)
def handle_process_request(result, imageryrequest_id):
    try:
        imagery_request = ImageryRequest.objects.get(pk=imageryrequest_id)
    except ImageryRequest.DoesNotExist:
        logger.critical(
            "This shouldn't have happened. Imagery Request {} does not exist.".format(
                imageryrequest_id
            )
        )

    if result == "FINISHED":
        # Send notification that this imagery request has finished
        Notification.objects.create(
            receiver=imagery_request.cadastre.farm.user,
            content=(
                "Запрос №{}: снимки для кадастра с номером {} успешно обработаны!"
            ).format(imagery_request.pk, imagery_request.cadastre.cad_number),
        )

        imagery_request.fetch_result_after_success()
        imagery_request.status = FINISHED
        imagery_request.save()
    elif result == "WAITING":
        imagery_request.status = WAITING
        imagery_request.requested_date += datetime.timedelta(days=1)
        imagery_request.save()

        if (
            ImageryRequest.objects.filter(
                cadastre=imagery_request.cadastre,
                requested_date=imagery_request.requested_date,
            )
            .exclude(Q(status__exact=FAILED) | Q(status__exact=FREE_EXPIRED))
            .exists()
        ):
            logger.info(
                "The cadastre {} is already in the queue for image processing.".format(
                    imagery_request.cadastre.pk
                )
            )
            Notification.objects.create(
                receiver=imagery_request.cadastre.farm.user,
                content=(
                    "Запрос №{} удален: кадастр с номером {}"
                    " уже на очереди в обработке."
                ).format(imagery_request.pk, imagery_request.cadastre.cad_number),
            )
            imagery_request.delete()
            return

        Notification.objects.create(
            receiver=imagery_request.cadastre.farm.user,
            content=(
                "Запрос №{}: Нет доступных снимков для кадастра с номером {}! Каждый"
                " день мы будем проверять наличие новых снимков на данный кадастр."
            ).format(imagery_request.pk, imagery_request.cadastre.cad_number),
        )

        imagery_request.start_image_processing(immediate=False)

    else:
        logger.critical("Imagery Request #{} FAILED!".format(imagery_request.pk))
        imagery_request.status = FAILED
        imagery_request.save()
