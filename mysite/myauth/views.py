from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.checks import messages
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _, ngettext
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from random import random
from django.views.generic import TemplateView, CreateView, RedirectView, ListView, DetailView, UpdateView, DeleteView
from django.views.decorators.cache import cache_page
from .forms import ProfileForm, AvatarForm
from .models import Profile


# def login_view(request: HttpRequest):
#     if request.method == "GET":
#         if request.user.is_authenticated:
#             return redirect('/admin/')
#
#         return render(request, 'myauth/login.html')
#
#     username = request.POST['username']
#     password = request.POST['password']
#
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return redirect('/admin/')
#
#     return render(request, 'myauth/login.html', {'error': 'Invalid login credentials'})


# def logout_view(request: HttpRequest) -> HttpResponse:
#     logout(request)
#     return redirect(reverse('myauth:login'))


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register-login.html"
    success_url = reverse_lazy("myauth:about-me")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.POST
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response

    def get_success_url(self):
        return reverse_lazy("myauth:about-me")


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"
    model = Profile
    form_class = AvatarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.request.user.profile)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect(reverse("myauth:about-me"))
        return self.render_to_response(self.get_context_data(form=form))


class MyLogoutView(RedirectView):
    pattern_name = "myauth:login"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


class ProfileListView(LoginRequiredMixin, ListView):
    template_name = "myauth/profile_list.html"
    context_object_name = "profiles"
    queryset = Profile.objects.select_related('user').all()


class ProfileDetailsView(LoginRequiredMixin, DetailView):
    template_name = "myauth/profile_details.html"
    model = User
    context_object_name = "users"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("myauth:profile_details", kwargs={"pk": self.object.pk})


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "myauth/profile_confirm_delete.html"
    success_url = reverse_lazy("myauth:profile_list")

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class HelloView(View):
    welcome_message = _("Welcome to my site!")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h>"
        )
