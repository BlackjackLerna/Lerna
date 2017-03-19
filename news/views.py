from django.views import generic

from .models import News


class IndexView(generic.ListView):
    queryset = News.objects.filter(visible=True).order_by('-created_at')
    template_name = 'news/list.html'
    allow_empty = True
    paginate_by = 10
    paginate_orphans = 1


class DetailView(generic.DetailView):
    queryset = News.objects.filter(visible=True)
    template_name = 'news/item.html'
