from django.urls import include, path, reverse_lazy
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView


handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'
handler500 = 'core.views.wrong_server'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('', include('blog.urls')),
]
