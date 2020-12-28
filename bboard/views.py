from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import BbForm, AuthUserForm, RegisterUserForm, RubricForm, SearchRubric, ImgForm
from .models import Bb, Rubric, Comment


class BbIndexView(TemplateView):
    template_name = 'bboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        context['bbs'] = Bb.objects.all()
        return context


class ClientRoom(LoginRequiredMixin, TemplateView):
    template_name = 'bboard/client_room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BboardLoginView(LoginView):
    template_name = 'bboard/login.html'
    initial = {'username': '', 'password': ''}
    form_class = AuthUserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy('bboard:client_room')


class BboardLogoutView(LogoutView):
    next_page = 'bboard:index'


class RegisterUserView(CreateView):
    model = User
    template_name = 'bboard/register_page.html'
    form_class = RegisterUserForm

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        auth_user = authenticate(username=username, password=password)
        login(self.request, auth_user)
        transaction.commit()
        return form_valid

    def get_success_url(self):
        return reverse('bboard:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BbDetailView(DetailView):
    model = Bb
    template_name = 'bboard/detail_bb.html'
    pk_url_kwarg = 'bb_id'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_bb = Bb.objects.get(pk=self.kwargs['bb_id'])
        context['rubrics'] = Rubric.objects.all()
        context['comments'] = Comment.objects.all()
        context['current_bb'] = current_bb
        context['latest_comments_list'] = current_bb.comment_set.order_by('-id')[:10]
        return context


class ByRubricListView(ListView):
    template_name = 'bboard/by_rubric.html'
    pk_url_kwarg = 'rubric_id'
    context_object_name = 'bbs'

    def get_queryset(self):
        return Bb.objects.filter(rubric=self.kwargs['rubric_id'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        context['current_rubric'] = Rubric.objects.get(pk=self.kwargs['rubric_id'])
        return context


class BbCreateView(LoginRequiredMixin, CreateView):
    template_name = 'bboard/create.html'
    form_class = BbForm
    initial = {'price': 0.0}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.save()
        transaction.commit()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bboard:detail_bb', kwargs={'bb_id': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context


class RubricCreateView(LoginRequiredMixin, CreateView):
    template_name = 'bboard/create_a_rubric.html'
    form_class = RubricForm

    def form_valid(self, form):
        form.save()
        transaction.commit()
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('bboard:by_rubric', kwargs={'rubric_id': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BbEditView(LoginRequiredMixin, UpdateView):
    template_name = 'bboard/edit.html'
    form_class = BbForm
    model = Bb
    pk_url_kwarg = 'bb_id'

    def form_valid(self, form):
        form.save()
        transaction.commit()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bboard:detail_bb', kwargs={'bb_id': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context


class BbDeleteView(LoginRequiredMixin, DeleteView):
    model = Bb
    template_name = 'bboard/delete.html'
    pk_url_kwarg = 'bb_id'

    def get_success_url(self):
        return reverse('bboard:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context


class RubricDeleteView(LoginRequiredMixin, DeleteView):
    model = Rubric
    template_name = 'bboard/delete_rubric.html'
    pk_url_kwarg = 'rubric_id'

    def get_success_url(self):
        return reverse('bboard:index')

    def get_context_data(self, **kwargs):
        q = Q(rubric__name=self.object.name)
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        context['bbs'] = Bb.objects.filter(q)
        return context


@login_required()
def leave_comment(request, bb_id):
    b = Bb.objects.get(id=bb_id)
    b.comment_set.create(author_name=request.user, comm_text=request.POST['text'])
    return redirect(reverse('bboard:detail_bb', kwargs={'bb_id': b.id}))


def rubrics(request):
    RubricFormSet = modelformset_factory(Rubric, fields='__all__', can_delete=True, extra=0)

    if request.method == 'POST':
        formset = RubricFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('bboard:index')
        else:
            transaction.rollback()
            return redirect('bboard:add_rubric_formset')

    else:
        formset = RubricFormSet()
    context = {'formset': formset}
    return render(request, 'bboard/rubrics.html', context)


def process_search_results(request):
    if request.method == 'POST':
        sf = SearchRubric(request.POST)
        if sf.is_valid():
            keyword = sf.cleaned_data['keyword']
            rubric_id = sf.cleaned_data['rubric'].pk
            bbs = Bb.objects.filter(rubric=rubric_id, title__iexact=keyword)
            context = {'bbs': bbs}
            return render(request, 'bboard/process_search_results.html', context)
    sf = SearchRubric()
    context = {'form': sf}
    return render(request, 'bboard/search_bb.html', context)


class ImgCreateView(CreateView):
    template_name = 'bboard/add_file.html'
    form_class = ImgForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bboard:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context
