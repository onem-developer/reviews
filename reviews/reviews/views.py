import onemsdk
import jwt
import requests


from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views.generic import View as _View

from onemsdk.schema.v1 import (
    Response, Menu, MenuItem, Form, FormItem, FormItemType, FormMeta
)

from .models import AppAdmin


class View(_View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *a, **kw):
        return super(View, self).dispatch(*a, **kw)

    def get_user(self):
        token = self.request.headers.get('Authorization')
        if token is None:
            raise PermissionDenied

        data = jwt.decode(token.replace('Bearer ', ''), key='87654321')
        user, created = User.objects.get_or_create(id=data['sub'], username=str(data['sub']))
        user.is_admin = data['is_admin']

        return user

    def to_response(self, content):
        response = Response(content=content)

        return HttpResponse(response.json(), content_type='application/json')

class HomeView(View):
    http_method_names = ['get', 'post']
    pass

