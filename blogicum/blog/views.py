from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models.functions import Now
from blog.models import Post, Category, User, Comment
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    ListView,
)
from django.urls import reverse
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin
)
from .forms import (
    PostForm,
    CommentForm,
)


# ФУНКЦИИ, МИКСИНЫ, КОНСТАНТЫ.
class PostMixin:

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class CommentMixin:

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['pk']]
        )

    def dispatch(self, request, *args, **kwargs):
        coment = get_object_or_404(
            Comment,
            id=self.kwargs['comment_id']
        )
        if coment.author != self.request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['pk']
            )
        return super().dispatch(request, *args, **kwargs)


class AddAuthorMixin:

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostQuerySet:

    def get_queryset(self):
        return Post.objects.select_related(
            'author',
            'location',
            'category'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date').all()


POST_LIST = Post.objects.select_related('category').filter(
    is_published=True,
    category__is_published=True,
    pub_date__lte=Now())

CATEGORY_LIST = Category.objects.filter(is_published=True)


# РАБОТА С ПОСТАМИ.
class PostDetailView(DetailView):

    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, AddAuthorMixin, PostMixin, CreateView):

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username,
        })


class PostUpdateView(OnlyAuthorMixin, AddAuthorMixin, PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'pk': self.object.pk
        })


class PostDeleteView(OnlyAuthorMixin,
                     PostMixin, LoginRequiredMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username,
        })


# РАБОТА С КОММЕНТАРИЯМИ.
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    pass


# РАБОТА С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ.

class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class ProfileListView(PostQuerySet, ListView):
    paginate_by = 10
    template_name = 'blog/profile.html'
    model = Post

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        queryset = Post.objects
        self.profile = get_object_or_404(User,
                                         username=self.kwargs['username'])

        queryset = queryset.filter(
            author=self.profile
        ).annotate(comment_count=Count('comments')).order_by(
            '-pub_date')
        if self.request.user != self.profile:
            queryset = super().get_queryset().annotate(
                comment_count=Count('comments'))

        return queryset

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=self.get_object()
        )


# НАРАБОТКИ ПРОШЛОГО СПРИНТА.


class PostListView(PostQuerySet, ListView):
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        return super().get_queryset().annotate(comment_count=Count('comments'))


class CategoryListView(PostQuerySet, ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().get_queryset().filter(
            category__slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
