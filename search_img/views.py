import base64
from email.policy import HTTP
from http import HTTPStatus
import http
from http.client import OK, HTTPResponse
import json
import random
import re
import shutil
import tempfile
import urllib
from io import BytesIO, StringIO
from sys import getsizeof
from typing import Any
from urllib import response
from urllib.request import Request, urlopen, urlretrieve
from weakref import proxy

import PIL
from PIL import Image as PIL_Image
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import requests
from bs4 import BeautifulSoup
import http.client as http_client

from config.settings import PIXELS_API, MEDIA_URL
from .forms import SearchForm, MyForm
from .services import search_image, save_images
from .models import Image, Pixels

""" my proxi """
PROXY = 'http://rs4dmz:patv3!Sj@185.237.219.170:64444'


# return self func name
import inspect
myself = lambda: inspect.stack()[0][3]


""" checking working proxie for url """
def check_proxies(url="https://pexels.com"):
    proxie_list = []
    with open("proxies-https.txt", "r") as file:
        lines = file.readlines()
        proxie_list = [line.rstrip() for line in lines]
        random.shuffle(proxie_list)

    print(f"==> {myself}: proxie len: {len(proxie_list)}")
    for proxy in proxie_list:
        response = proxy_request(url, proxy)
        if (response) and (response.ok):
            print(proxy)

    return False


""" scan free-proxy-list.net and save to file annonymous proxy 
    https_need - if needed 443 protocol
"""
def get_proxies(https_need: bool=False):

    res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
    # print(f"==> <{myself}> response: {res.status_code}")
    soup = BeautifulSoup(res.text,"lxml")
    with open(f"proxies{'-https' if https_need else ''}.txt", "w") as file:
        for items in soup.select(".fpl-list tbody tr"):
            
            row = items.select("td")
            # print(f"==> <{myself}> table row: {row}")

            https_present = (row[6].text == "yes")
            anonymous = (row[4].text == "anonymous")
            proxy = ':'.join([item.text for item in items.select("td")[:2]])
            print(f"==> <{myself}> anonymous: {anonymous} https: {https_present} host {proxy}")

            write_row = 0
            if anonymous:
                write_row = 1                
                if not (https_need and https_present):
                    write_row = 0

            if write_row:
                file.write(f"{proxy}\n")


""" request through proxi 
    url - url
    proxy - string with user:passwd@url:port
    **kwargs - other params for request
"""
def proxy_request(url, proxy=PROXY, **kwargs):
    # http_client.HTTPConnection.debuglevel = 0
    response = False
    try:
        # print(f"==> check proxy <{myself}>: {proxy}")
        proxies = {"http": proxy, "https": proxy}
        response = requests.get(url, proxies=proxies, timeout=5, allow_redirects=False, **kwargs)
        print(f"==> SUCCESS: Proxy currently being used: {proxy}")
    except requests.exceptions.RequestException as e:
        # print(f"==> check proxy except <{myself}>: {e}")
        pass

    # http_client.HTTPConnection.debuglevel = 0
    return response

""" forget fo what )"""
def make_thumbnail(image: PIL_Image, w: int = 280, h: int = 200) -> PIL_Image:
    return PIL_Image.open(image.origin).thumbnail((w, h))

""" cache image from image description to inner db info and image as file 
    id - external id from deliver
    alt - description
    origin_url - url full size image
"""
def save_new_image_to_cache(id_key: int, alt: str, origin_url: str):

    headers = {'Authorization': PIXELS_API}
    response = proxy_request(origin_url, proxy=PROXY, stream=True, headers=headers)

    if response and response.ok:
        try:
            obj = Pixels(id=id_key, alt=alt)
            obj.origin.save(f'{id_key}.jpg', response.raw)
            obj.save()
            return obj
        except ObjectDoesNotExist:
            return None

    return None


def check_image_in_cache(photos_list) -> list:

    # print("--> INFO <check_image_in_cache>: check_image_in_cache..")
    result_list = []
    for photo in photos_list:
        photo_id = photo.get("id")
        try:
            cached_image = Pixels.objects.get(id=photo_id)
            # thumbnail = make_thumbnail(cached_image.origin)
            result_list.append(
                {
                    "id": photo_id,
                    "alt": cached_image.alt,
                    "tiny": photo.get("src").get("tiny"),
                    "origin": cached_image.origin.url,
                }
            )
        except ObjectDoesNotExist:
            result_list.append(
                {
                    "id": photo_id,
                    "alt": photo.get("alt", ""),
                    "tiny": photo.get("src").get("tiny"),
                    "origin": photo.get("src").get("original")
                }
            )
    # print("--> INFO <check_image_in_cache>: list photos", result_list)
    return result_list


"""
{
'id': 846350,
'width': 3456,
'height': 2304,
'url': 'https://www.pexels.com/photo/photography-of-mountains-near-body-of-water-846350/',
'photographer': 'Belle Co', 'photographer_url': 'https://www.pexels.com/@belle-co-99483',
'photographer_id': 99483,
'avg_color': '#5E7068',
'src': {
    'original': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg',
    'large2x': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
    'large': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg?auto=compress&cs=tinysrgb&h=650&w=940',
    'medium': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg?auto=compress&cs=tinysrgb&h=350',
    'small': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg?auto=compress&cs=tinysrgb&h=130',
    'portrait': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=800',
    'landscape': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200',
    'tiny': 'https://images.pexels.com/photos/846350/pexels-photo-846350.jpeg?auto=compress&cs=tinysrgb&dpr=1&fit=crop&h=200&w=280'
},
'liked': False,
'alt': 'Photography of Mountains Near Body of Water'
}
"""

""" Check host access (russian restrict) """
def check_forbidden_host(host: str):
    return True

""" If cannot acces directly to site -> convert img url to content image through proxy request """
def create_image_thumbnail(urls: list):

    if check_forbidden_host("https://pexels.com"):

        for i in len(urls)-1:
            img_url = urls[i]
            response = proxy_request(img_url.tiny, proxy=PROXY, stream=True)
            response.raw.decode_content = True # handle spurious Content-Encoding

            temp_image = Image.open(response.raw)
            temp_buffer = StringIO.StringIO()
            temp_image.save(temp_buffer, "PNG")
            thumbnail = temp_buffer.getvalue().encode("base64")
            temp_buffer.close()
            urls[i].tiny = thumbnail.split('\n')[0]


""" get list image description from stock for query 
    query - search string
    count - count images request
"""
def get_list_images_descriptions_from_stock(query: str, count: int):
    headers = {
        'Authorization': PIXELS_API, 
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
    }
    params = {'query': query, 'per_page': count, 'page': 1}

    url = 'https://api.pexels.com/v1/search'

    response = proxy_request(url, proxy=PROXY, params=params, headers=headers)
    
    if response and response.ok:
        photos = response.json().get("photos", [])
        return create_image_thumbnail(check_image_in_cache(photos))

    print("--> INFO: <get_list_images_descriptions_from_stock>: API pixels error response: ", response.status_code, response.reason)
    return []


class MyView(View):
    def get(self, request):
        context = {
            'form': MyForm(),
            'title': 'MyForm',
        }
        return render(request, "search_img/my_template.html", context)

    def post(self, request):
        # print("--> INFO: <MyView>: Incoming post request..")
        form = MyForm(request.POST)
        if form.is_valid():
            image_list = get_list_images_descriptions_from_stock(
                form.cleaned_data["query"],
                form.cleaned_data["count"]
            )
            context = {
                'form': MyForm(),
                'title': 'MyForm',
                'photo_urls': image_list,
            }
            return render(request, "search_img/my_template.html", context)


def cache_update(request):
    if request.method == "POST":
        payload = json.loads(request.body)
        # print('--> INFO <cache_update>:', payload)
        if not ("id_photo" in payload):
            print('--> ERR: Can`t get id param, redirect ..')
            return redirect('/')

        request_json_params = json.loads(request.body)
        id_photo = int(request_json_params.get("id_photo"))

        alt = request_json_params.get("alt")
        tiny_url = request_json_params.get("tiny")
        origin_url = request_json_params.get("origin")
        ''' very costly way sending raw data from js'''
        # image_data = request_json_params.get("image_raw")
        # image_data = re.sub("^data:image/png;base64,", "", image_data)
        # image_data = base64.b64decode(image_data)
        # image_data = BytesIO(image_data)
        #
        # with open('temp.io', "wb") as f:
        #     f.write(image_data.getbuffer())
        #
        # ready_image = PIL_Image.open('temp.io')
        # if not ready_image.verify():
        #     print('::::ERR Image not valid, redirect ..')
        #     return redirect('/')

        # image_64_encode = base64.encodebytes(bytes(image_string, 'utf-8'))
        # image_64_decode = base64.decodebytes(image_64_encode)
        # ready_image = PIL_Image.frombytes('RGB', (500, 500), image_64_decode)

        # ready_image = PIL_Image.frombytes('RGB', (500, 500), image_64_decode)
        # url = request_json_params.get("origin")
        # print('::::: parse POST data:', id_photo, alt, url)
        # url = 'https://www.krasplastic.ru/img/europress_card.png'
        # url = f"http://{''.join(url.split('//')[1])}"
        # print(url)
        # tmp_file, _ = urlretrieve(url)
        # image_field = SimpleUploadedFile(f"{id_photo}.jpg", open(tmp_file, "rb").read())
        """ end load image through buffer from js"""

        obj = save_new_image_to_cache(id_key=id_photo, alt=alt, origin_url=origin_url)
        if obj:
            context = {
                "id": obj.id,
                "alt": obj.alt,
                "tiny": tiny_url,
                # "tiny": make_thumbnail(response.origin),
                "origin": obj.origin.url,
                }
        else:
            #  fault load image from url, return incoming parameters
            context = {"id": id_photo, "alt": alt, "tiny": tiny_url, "origin": origin_url}

        # print("--> INFO: ", context)
        # return HttpResponse(context, content_type='application/json')
        return JsonResponse(data=context, safe=False)


class SearchImageView(View):
    async def get(self, request):
        return await sync_to_async(render)(request, 'search_img/index.html', {'form': SearchForm()})

    async def post(self, request):
        form = SearchForm(request.POST)
        images = []
        if form.is_valid():
            images = await search_image(form.cleaned_data['query'], form.cleaned_data['count'])
        return await sync_to_async(render)(
            request, 'search_img/index.html', {'form': SearchForm(), 'images': images}
        )


@login_required
def search_save(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        images = []
        if form.is_valid():
            images = async_to_sync(save_images)(
                request.user.id,
                form.cleaned_data['query'],
                form.cleaned_data['count']
            )
        return render(
            request, 'search_img/index.html', {'form': SearchForm(), 'images': images}
        )


class ListImageView(View):
    async def get(self, request):
        user = await sync_to_async(request.user.id)()
        print(user)
        images = Image.objects.filter()
        return await sync_to_async(render)(
            request, 'search_img/list_images.html', {'images': images}
        )
