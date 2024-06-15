from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from blog.models import Category, Comment, Post, User
from core.constants import POST_ORDERING
from core.mixins import (
    CommentMixin,
    PostMixin,
    AddAuthorMixin,
    PostQuerySet,
    OnlyAuthorMixin
)
from .forms import (
    CommentForm,
    PostForm,
)


# РАБОТА С ПОСТАМИ.
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=self.kwargs["pk"])
        if instance.author != self.request.user and not instance.is_published:
            raise Http404("Страница не найдена")
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin,
                     AddAuthorMixin, PostMixin, CreateView):
    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={
                "username": self.request.user.username,
            },
        )


class PostUpdateView(OnlyAuthorMixin,
                     AddAuthorMixin, PostMixin, UpdateView):
    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={"username": self.request.user.username})

    def handle_no_permission(self):
        return redirect("blog:post_detail", pk=self.kwargs["pk"])


class PostDeleteView(OnlyAuthorMixin,
                     PostMixin, LoginRequiredMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={
                "username": self.request.user.username,
            },
        )


# РАБОТА С КОММЕНТАРИЯМИ.
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = "blog/comment.html"
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", args=[self.kwargs["pk"]])


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    pass


# РАБОТА С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ.


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    fields = ("username", "first_name", "last_name", "email")

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={"username": self.request.user.username})


class ProfileListView(PostQuerySet, ListView):
    paginate_by = 10
    template_name = "blog/profile.html"
    model = Post

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        queryset = Post.objects
        self.profile = get_object_or_404(User,
                                         username=self.kwargs["username"])

        queryset = (
            queryset.filter(author=self.profile)
            .annotate(comment_count=Count("comments"))
            .order_by(POST_ORDERING)
        )
        if self.request.user != self.profile:
            queryset = super().get_queryset().annotate(
                comment_count=Count("comments"))

        return queryset

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs),
                    profile=self.get_object())


# НАРАБОТКИ ПРОШЛОГО СПРИНТА.


class PostListView(PostQuerySet, ListView):
    paginate_by = 10
    template_name = "blog/index.html"

    def get_queryset(self):
        return super().get_queryset().annotate(comment_count=Count("comments"))


class CategoryListView(PostQuerySet, ListView):
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = 10
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return (
            super().get_queryset().filter(
                category__slug=self.kwargs["category_slug"])
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context
