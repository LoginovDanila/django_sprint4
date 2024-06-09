from django.shortcuts import get_object_or_404, render, redirect
from django.db.models.functions import Now
from blog.models import Post, Category, User, Comment
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView
)
from django.core.paginator import Paginator
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


def profile(request, username):
    template_name = 'blog/profile.html'
    profile = User.objects.get(username=username)
    post_list = Post.objects.select_related(
        'category').select_related(
        'author').filter(
        is_published=True,
        category__is_published=True,
        author__username=username)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'profile': profile
    }
    return render(request, template_name, context)


# НАРАБОТКИ ПРОШЛОГО СПРИНТА.

def index(request):
    template_name = 'blog/index.html'
    paginator = Paginator(POST_LIST, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category_info = get_object_or_404(CATEGORY_LIST, slug=category_slug)
    post_list = POST_LIST.filter(category__slug=category_slug)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category_info
    }
    return render(request, template_name, context)
