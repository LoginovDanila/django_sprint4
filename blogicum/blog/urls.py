from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # ОБЩИЕ СТРАНИЦЫ
    path('',
         views.index,
         name='index'
         ),
    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'
         ),
    # РАБОТА С ПРОФИЛЕМ
    path('profile/<username>/',
         views.profile,
         name='profile'
         ),
    path(
        'edit_profile/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),
    # РАБОТА С ПОСТАМИ
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post',
         ),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'
         ),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'
         ),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'
         ),
    # РАБОТА С КОММЕНТАРИЯМИ
    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'
         ),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'
         ),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'
         ),
]
