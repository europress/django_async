import requests
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View

from config.settings import PIXELS_API
from .forms import SearchForm, MyForm
from .services import search_image, save_images
from .models import Image


def get_images(query, count):
    headers = {'Authorization': PIXELS_API}
    params = {'query': query, 'per_page': count, 'page': 1}
    url = 'https://api.pexels.com/v1/search'

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        photos = response.json().get("photos", [])
        return [{"tiny": url.get("src").get("tiny"), "original": url.get("src").get("original")} for url in photos]
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
            context = {
                'form': MyForm(),
                'title': 'MyForm',
                'photo_urls': get_images(form.cleaned_data["query"], form.cleaned_data["count"])
            }
            return render(request, "search_img/my_template.html", context)


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
