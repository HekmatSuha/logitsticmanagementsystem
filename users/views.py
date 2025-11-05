from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission, User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import StyledAuthenticationForm, UserRegistrationForm


class UserListView(LoginRequiredMixin, ListView):
    template_name = "users/list.html"
    model = User
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by("username")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        users_list = list(ctx["users"])
        selected_user = None
        selected_id = self.request.GET.get("id")
        if selected_id:
            selected_user = next((user for user in users_list if str(user.pk) == selected_id), None)
        if not selected_user and users_list:
            selected_user = users_list[0]
        available_roles = (
            User.objects.values_list("groups__name", flat=True)
            .exclude(groups__name__isnull=True)
            .distinct()
        )
        ctx.update(
            {
                "search_query": self.request.GET.get("q", "").strip(),
                "selected_user": selected_user,
                "role_choices": [role for role in available_roles if role],
                "selected_roles": list(selected_user.groups.values_list("name", flat=True)) if selected_user else [],
                "selected_permissions": (
                    list(
                        Permission.objects.filter(user=selected_user)
                        .values_list("name", flat=True)
                        .order_by("name")
                    )
                    if selected_user
                    else []
                ),
            }
        )
        return ctx


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


class RegisterView(CreateView):
    template_name = "registration/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
