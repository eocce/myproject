# myapp/data_processing.py

import os
import zipfile
import requests
from .models import RemoteSensingData



def publish_data_to_geoserver(workspace, datastore, layer):
    geoserver_url = 'http://localhost:8080/geoserver/rest'  # GeoServer 的 REST API URL
    username = 'admin'  # GeoServer 的用户名
    password = 'geoserver'  # GeoServer 的密码

    # 创建工作空间
    requests.post(f'{geoserver_url}/workspaces', json={'workspace': {'name': workspace}}, auth=(username, password))

    # 创建数据存储
    requests.post(f'{geoserver_url}/workspaces/{workspace}/datastores', json={'dataStore': {'name': datastore}},
                  auth=(username, password))

    # 发布图层
    requests.post(f'{geoserver_url}/workspaces/{workspace}/datastores/{datastore}/featuretypes',
                  json={'featureType': {'name': layer}}, auth=(username, password))

def query_data(time=None, coordinates=None, polygon=None):
    # 根据给定的条件查询遥感数据
    queryset = RemoteSensingData.objects.all()

    if time is not None:
        queryset = queryset.filter(time=time)

    if coordinates is not None:
        queryset = queryset.filter(latitude=coordinates[0], longitude=coordinates[1])

    # 如果给定了多边形，你需要使用一个更复杂的查询来找到位于多边形内的数据
    # 这可能需要使用 Django 的 GIS 功能，这超出了本示例的范围

    return queryset
