from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import CustomLoginView, ProfileUpdateView, RegisterView, verify_account, \
    CustomPasswordResetCompleteView, CustomPasswordResetConfirmView, CustomPasswordResetDoneView, \
    CustomPasswordResetView, UserListView

app_name = UsersConfig.name


urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<int:user_pk>/', verify_account, name='verify_account'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password/reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('users_list/', login_required(UserListView.as_view()), name='users_list'),
]


