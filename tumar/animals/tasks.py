import requests
import django.utils.timezone as tz
import pytz
import json


from datetime import datetime as dt
from django.conf import settings

from .models import Farm, Animal
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


@app.task
def task_download_latest_battery_percentage():
    farms_attrs = Farm.objects.values_list("id", "api_key")

    for farm in farms_attrs:
        if farm[1]:
            url = settings.GET_BATTERY_CHARGE_URL
            headers = {"Content-type": "application/json", "Accept": "application/json"}
            payload = {
                "key": settings.CHINESE_API_KEY,
                "farmid": farm[1],
            }

            r = requests.post(url, data=json.dumps(payload), headers=headers)

            if r.status_code != requests.codes.ok:
                r.raise_for_status()
            response_data = r.json()
            print(response_data)
            for item in response_data["data"]:
                if item.get("voltage", None):
                    my_tz = pytz.timezone("Asia/Almaty")
                    my_date = dt.strptime(item["lastupdate"], "%Y-%m-%d %H:%M:%S")
                    time = tz.make_aware(my_date, my_tz)

                    the_animal = Animal.objects.get(imei=item["imei"])

                    if the_animal.updated < time:
                        the_animal.battery_charge = item["voltage"]
                        if not the_animal.imsi:
                            the_animal.imsi = item["imsi"]
                        the_animal.save()
