from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('item_detail/<int:id>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('comment_list/<int:id>/', views.CommentListView.as_view(), name='comment_list'),
    path('comment_detail/<int:id>/', views.CommentDetailView.as_view(), name='comment_detail'),
    path('rating/<int:id>/', views.RatingView.as_view(), name='rating'),
]

