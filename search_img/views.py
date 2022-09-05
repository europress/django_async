import base64
import json
import re
import shutil
import tempfile
import urllib
from io import BytesIO, StringIO
from sys import getsizeof
from typing import Any
from urllib.request import urlopen, urlretrieve

import PIL
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import requests

from config.settings import PIXELS_API, MEDIA_URL
from .forms import SearchForm, MyForm
from .services import search_image, save_images
from .models import Image, Pixels


def make_thumbnail(image: PIL.Image, w: int = 280, h: int = 200) -> PIL.Image:
    return PIL.Image.open(image.origin).thumbnail((w, h))


def save_new_image_to_cache(id_key: int, alt: str, origin_url: str) -> Pixels | None:
    """ load original sized image and save to cache """

    headers = {'Authorization': PIXELS_API}
    response = requests.get(origin_url, stream=True, headers=headers)

    if response.status_code == 200:
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
                    "in_cache": True,
                }
            )
        except ObjectDoesNotExist:
            result_list.append(
                {
                    "id": photo_id,
                    "alt": photo.get("alt", ""),
                    "tiny": photo.get("src").get("tiny"),
                    "origin": photo.get("src").get("original"),
                    "in_cache": False,
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


def get_list_images_descriptions_from_stock(query, count):
    headers = {'Authorization': PIXELS_API}
    params = {'query': query, 'per_page': count, 'page': 1}
    url = 'https://api.pexels.com/v1/search'

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        photos = response.json().get("photos", [])
        return check_image_in_cache(photos)
    return []


class MyView(View):
    def get(self, request):
        context = {
            'form': MyForm(),
            'title': 'MyForm',
        }
        return render(request, "search_img/my_template.html", context)

    def post(self, request):
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
        # ready_image = PIL.Image.open('temp.io')
        # if not ready_image.verify():
        #     print('::::ERR Image not valid, redirect ..')
        #     return redirect('/')

        # image_64_encode = base64.encodebytes(bytes(image_string, 'utf-8'))
        # image_64_decode = base64.decodebytes(image_64_encode)
        # ready_image = PIL.Image.frombytes('RGB', (500, 500), image_64_decode)

        # ready_image = PIL.Image.frombytes('RGB', (500, 500), image_64_decode)
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
