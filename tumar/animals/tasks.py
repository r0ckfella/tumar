from .models import Farm
from .utils import download_geolocations
from ..celery import app


@app.task
def task_download_latest_geolocations():
    """
    Downloads geolocations from chinese API
    """
    farms_attrs = Farm.objects.values_list("id", "api_key")

    for farm in farms_attrs:
        if farm[1]:
            download_geolocations(farm[0], farm[1])
