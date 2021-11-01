from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from contrib.views.generic import DblogDetailView, DblogListView
from .models import Post
from .forms import PostForm


# Create your views here.
class PostList(DblogListView):
    model = Post
    form_class = PostForm
    actions = ['example']
    search_fields = ['title__icontains',
                     'content__icontains',
                     'profile__username__icontains']

    def post(self, request, *args, **kwargs):
        if 'new_post' in request.POST and request.user.has_perm('blog.add_post'):
            form = self.get_form()
            if form.is_valid():
                instance = form.save(commit=False)
                instance.profile = request.user
                instance.save()
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        action_result = self.handle_actions(request)
        return action_result or self.reload_page()

    def example(self, request, posts):
        messages.success(
            request, _(f'Örnek aksiyon, seçilen {len(posts)} \
                        gönderiye başarıyla uygulandı'))


class PostDetail(DblogDetailView):
    model = Post
