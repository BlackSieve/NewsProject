from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.conf import settings


from .models import Post, Category, Comment
from datetime import datetime
from .filters import PostFilter
from .forms import PostForms, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class PostAuth(LoginRequiredMixin, TemplateView):
    form_class = PostForms
    model = Post


class PostList(ListView):
    model = Post
    ordering = '-date'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now']=datetime.utcnow()
        context['next_sale']=None
        context['filterset']=self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(PermissionRequiredMixin,CreateView):
    permission_required = ('news.add_post')
    form_class = PostForms
    model = Post
    template_name = 'post_edit.html'
    context_object_name = 'create'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user.author
        if self.request.path == '/news/articles/create/':
            post.post_news = 'SE'
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForms
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin,DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news')
    permission_required = ('news.delete_post',)


class PostSearch(ListView):
    model = Post
    ordering = '-date'
    template_name = 'post.html'
    context_object_name = 'news'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class ArticlesCreate(CreateView):
    permission_required = 'news.add_post'
    from_class = Post


class CategoryListView(PostList):
    model = Post
    template_name = 'news/category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.category = get_object_or_404(Category, id = self.kwargs['pk'])
        queryset = queryset.filter(category = self.category).order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category']=self.category
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    massage = "Вы успешно подписались на рассылку объявлений по категории"
    return render(request,'news/subscribe.html', {'category':category, 'massage':massage})



class CommentCreatView(CreateView, LoginRequiredMixin):
    form_class = CommentForm
    model = Comment
    template_name = 'comment_create.html'
    context_object_name = 'comment'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = self.kwargs['pk']
        comment.user = self.request.user
        comment.save()
        send_mail(
            subject=f'New Comment on "{comment.post.title}"',
            message=f'Вам был оставлен отклик "{comment.text}" пользователем {self.request.user.username.title()} на ваше объявление "{comment.post.title}"',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[comment.post.author.user.email]
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post']=Post.objects.get(id = self.kwargs['pk'])
        return context