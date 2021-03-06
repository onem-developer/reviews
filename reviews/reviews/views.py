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
from django.shortcuts import get_object_or_404

from onemsdk.schema.v1 import (
    Response, Menu, MenuItem, Form, FormItem, FormItemType, FormMeta
)

from .models import Item, Comment


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

        return user

    def to_response(self, content):
        response = Response(content=content)

        return HttpResponse(response.json(), content_type='application/json')


class HomeView(View):
    http_method_names = ['get']

    def get(self, request):
        menu_items = []
        # check if an item has just been rated
        rating_added = cache.get('rating_added')
        if rating_added:
            menu_items.append(
                MenuItem(description='Rating of {value} was added to {item}'.format(
                    value=rating_added['rating_value'],
                    item=rating_added['rated_item']))
                )
            cache.set('rating_added', None)

        items = Item.objects.all()  # local sqlite DB is already populated
        menu_items.extend([
            MenuItem(description=item.name,
                     method='GET',
                     path=reverse('item_detail', args=[item.id]))
            for item in items
        ])

        content = Menu(body=menu_items, header=u'REVIEWS HOME')
        return self.to_response(content)


class ItemDetailView(View):
    http_method_names = ['get', 'post']

    def get(self, request, id):
        item = get_object_or_404(Item, id=id)
        comments_count = Comment.objects.filter(item=item).count()

        menu_items = [
            MenuItem(description=item.item_description),
            MenuItem(description=u'Rating: {rating}'.format(rating=item.rating))
        ]

        menu_items.extend([
            MenuItem(description=u'Comments ({count})'.format(count=comments_count),
                     method='GET',
                     path=reverse('comment_list', args=[item.id]))
        ])

        # TODO: mention in the READ.ME file that the Rate options is only displayed
        # for an user who doesn't own the viewed item
        if item.item_owner != self.get_user():
           menu_items.extend([
               MenuItem(description=u'Rate',
                        method='GET',
                        path=reverse('rating', args=[item.id, item.rating]))
           ])

        content = Menu(body=menu_items, header=item.name)
        return self.to_response(content)


class AddCommentView(View):
    http_method_names = ['get', 'post']

    def get(self, request, id):
        form_items = [
            FormItem(type=FormItemType.string,
                     name='comment_text',
                     description='Send your comment, no more than 200 characters.',
                     header='add comment',
                     footer='Reply with text')
        ]
        form = Form(body=form_items,
                    method='POST',
                    path=reverse('add_comment', args=[id]),
                    meta=FormMeta(confirmation_needed=False,
                                  completion_status_in_header=False,
                                  completion_status_show=False))
        return self.to_response(form)

    def post(self, request, id):
        item = Item.objects.get(id=id)
        comment_owner=self.get_user()
        text = self.request.POST['comment_text']
        new_comment = Comment.objects.create(
            item=item, text=text, comment_owner=comment_owner
        )
        new_comment.save()
        return HttpResponseRedirect(reverse('comment_list', args=[id]))


class CommentListView(View):
    http_method_names = ['get', 'post']

    def get(self, request, id):
        menu_items = [
            MenuItem(description='Add comment',
                     method='GET',
                     path=reverse('add_comment', args=[id])
            )
        ]

        item = Item.objects.get(id=id)
        comments = Comment.objects.filter(item=item)
        if comments:
            for comment in comments:
                menu_items.append(
                        MenuItem(description=u'{}..'.format(comment.text[:18]),
                             method='GET',
                             path=reverse('comment_detail', args=[comment.id]))
                )
        else:
            menu_items.append(
                MenuItem(description='This item has no comments yet.')
            )
        content = Menu(body=menu_items, footer='Reply MENU')

        return self.to_response(content)


class CommentDetailView(View):
    http_method_names = ['get', 'post']

    def get(self, request, id):
        # TODO: if viewing user is the comment owner - offer the option to
        # edit/delete the comment
        comment = get_object_or_404(Comment, id=id)
        content = Menu(
            body=[
                MenuItem(description=comment.text)
            ],
            header='comment',
            footer='MENU'
        )
        return self.to_response(content)


class RatingView(View):
    http_method_names = ['get', 'post']

    def get(self, request, id, new_rating=None):
        form_items = [
            FormItem(type=FormItemType.string,
                     name='rating_value',
                     description=u'\n'.join([
                         'Send your rating from 1 to 5.',
                         '1 is Poor, 5 is Excellent.'
                     ]),
                     header='add rating',
                     footer='Reply "1".."5"')
        ]
        form = Form(body=form_items,
                    method='POST',
                    path=reverse('rating', args=[id, new_rating]),
                    meta=FormMeta(confirmation_needed=False,
                                  completion_status_in_header=False,
                                  completion_status_show=False))
        return self.to_response(form)

    def post(self, request, id, new_rating):
        item = get_object_or_404(Item, id=id)
        rating = item.rating or 3
        new_rating = (rating + int(self.request.POST['rating_value'])) / 2
        item.rating = new_rating
        item.save()

        cache.set(
            'rating_added',
            {'rated_item': item.item_description,
             'rating_value': int(self.request.POST['rating_value'])}
        )

        return HttpResponseRedirect(reverse('home'))
