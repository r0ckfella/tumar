from celery import shared_task, states
from datetime import datetime, timedelta

from ..celery import app
from .models import ImageryRequest
from .serializers import ImageryRequestSerializer
from .geoserver import mapproxy, layer_create_tiff


def main_request_fetch(imagery_request, requested_date, date_amplitude=14, generate_bands=False):
    task_name = 'image_backend.process_main_request'
    cadastre = imagery_request.cadastre

    obj_serialized = ImageryRequestSerializer(imagery_request)

    result = app.signature(task_name,
                           args=(cadastre.geom.wkt,),
                           kwargs={
                               'target_date': str(requested_date),
                               'request_info': obj_serialized.data,
                               'date_amplitude': date_amplitude,
                               'generate_bands': generate_bands
                           },
                           queue=task_name,
                           priority=5,
                           )

    result_handler_task_name = 'imagery_requests.handle_process_request'
    handler_task = app.signature(result_handler_task_name,
                                 kwargs={
                                     "request_id": imagery_request.id

                                 },
                                 queue=result_handler_task_name)

    # If True, then plan ImageryRequest for future
    if requested_date > datetime.date(datetime.now()):
        (result | handler_task).apply_async(eta=requested_date)
    else:
        (result | handler_task).delay()


@shared_task(bind=True, ignore_result=True, name='imagery_requests.handle_process_request',
             queue='imagery_requests.handle_process_request')
def handle_process_request(self, result, request_id):
    try:
        imagery_request = ImageryRequest.objects.get(pk=request_id)
    except ImageryRequest.DoesNotExist:
        self.update_state(state=states.FAILURE)
        return 'IMAGERY_REQUEST_NOT_EXIST'

    # result = (success/failure, (results_dir, image_date)/None)
    if result[0]:
        results_dir, image_date = result[1]['results_dir'], result[1]['image_date']
        imagery_request.success(results_dir, image_date)

        # LAYER CREATION
        layer_create_tiff(imagery_request)
        mapproxy()
        self.update_state(state=states.SUCCESS)
        return 'IMAGERY_SUCCESSFULLY_FINISHED'
    else:
        # If failure -> resend request
        requested_date = imagery_request.requested_date
        date_amplitude = 14

        # PAST HANDLER
        if requested_date < datetime.date(datetime.now()):
            imagery_request.failure()
            self.update_state(state=states.SUCCESS)
            return 'IMAGERY_DATE_NOT_FOUND_IN_PAST'

        # NOW HANDLER
        elif requested_date == datetime.now().date():
            delta = timedelta(days=1)
            requested_date += delta
            date_amplitude = 2

        main_request_fetch(
            imagery_request=imagery_request,
            requested_date=requested_date,
            date_amplitude=date_amplitude,
        )
        self.update_state(state=states.SUCCESS)
        return 'IMAGERY_NOT_FOUND_WAITING_FOR_NEXT_DAY'
