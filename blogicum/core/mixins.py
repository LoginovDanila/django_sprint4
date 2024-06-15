from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from core.constants import POST_ORDERING
from blog.models import Comment, Post
from blog.forms import (
    PostForm,
)


class PostQuerySet:
    def get_queryset(self):
        return (
            Post.objects.select_related("author", "location", "category")
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .order_by(POST_ORDERING)
            .all()
        )


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"


class CommentMixin:
    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_success_url(self):
        return reverse("blog:post_detail", args=[self.kwargs["pk"]])

    def dispatch(self, request, *args, **kwargs):
        if get_object_or_404(Comment, id=self.kwargs[
                "comment_id"]).author != self.request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)


class AddAuthorMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user
