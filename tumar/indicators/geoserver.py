import os
import json
import requests

from geoserver.catalog import Catalog


def layer_create_tiff(request, name_part="_tumar_", root="/root/Rasters"):
    geo_url = (
        "http://geoserver:8080/geoserver/rest/"
        if os.getenv("DEFAULT_DB_HOST")
        else "https://geo.egistic.kz/geoserver/rest/"
    )
    cat = Catalog(geo_url, "admin", "UxeiJ5ree2riVoi")
    ws = cat.get_workspace("global")

    # Indicator layerization
    ndmi = "ndmi{}{}".format(name_part, request.id)
    ndvi = "ndvi{}{}".format(name_part, request.id)
    gndvi = "gndvi{}{}".format(name_part, request.id)
    clgreen = "clgreen{}{}".format(name_part, request.id)
    rgb = "rgb{}{}".format(name_part, request.id)
    layer1 = cat.get_layer(rgb)
    if layer1 is None:
        print("------start of creating layer-------")
        url1 = "{}/{}/ndmi.tiff".format(root, request.results_dir)
        url2 = "{}/{}/ndvi.tiff".format(root, request.results_dir)
        url3 = "{}/{}/gndvi.tiff".format(root, request.results_dir)
        url4 = "{}/{}/clgreen.tiff".format(root, request.results_dir)
        url5 = "{}/{}/rgb.tiff".format(root, request.results_dir)
        # url5 = "/root/Rasters/include_parents_rgb.tiff"
        cat.create_coveragestore(name=ndmi, data=url1, workspace=ws, overwrite=True)
        cat.create_coveragestore(name=ndvi, data=url2, workspace=ws, overwrite=True)
        cat.create_coveragestore(name=gndvi, data=url3, workspace=ws, overwrite=True)
        cat.create_coveragestore(name=clgreen, data=url4, workspace=ws, overwrite=True)
        cat.create_coveragestore(name=rgb, data=url5, workspace=ws, overwrite=True)
        check1 = "global:ndmi{}{}".format(name_part, request.id)
        that_layer1 = cat.get_layer(check1)
        that_style1 = cat.get_style("global:ndmi")
        that_layer1.default_style = that_style1

        check2 = "global:ndvi{}{}".format(name_part, request.id)
        that_layer2 = cat.get_layer(check2)
        that_style2 = cat.get_style("global:ndvi")
        that_layer2.default_style = that_style2

        check3 = "global:gndvi{}{}".format(name_part, request.id)
        that_layer3 = cat.get_layer(check3)
        that_style3 = cat.get_style("global:gndvi")
        that_layer3.default_style = that_style3

        check4 = "global:clgreen{}{}".format(name_part, request.id)
        that_layer4 = cat.get_layer(check4)
        that_style4 = cat.get_style("global:clgreen")
        that_layer4.default_style = that_style4

        cat.save(that_layer1)
        cat.save(that_layer2)
        cat.save(that_layer3)
        cat.save(that_layer4)

        print("Layers are created")


def mapproxy():
    # This initialises the Client with the settings passed. <port> has to be an integer.
    # tc = TeamCity('admin', 'astana2017', 'ci.egistic.kz')

    # data = tc.get_projects()
    # print(json.dumps(data, indent=4))

    url = "https://ci.openlayers.kz/httpAuth/app/rest/buildQueue/"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"buildTypeId": "mapproxy_util_upd_conf"})
    r = requests.post(
        url, headers=headers, data=data, auth=("admin", "astana2017"), timeout=10
    )
    print("r = ", r)
