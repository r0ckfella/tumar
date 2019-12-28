from .utils import download_geolocations
from ..celery import app


@app.task
def task_download_latest_geolocations():
    """
    Downloads geolocations from chinese API
    """
    download_geolocations()
