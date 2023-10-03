from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

app_name = 'study'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('room/<pk>/detail', views.RoomDetailView.as_view(), name='room'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', auth_view.LoginView.as_view(template_name='home/login.html', redirect_authenticated_user=True), name='login'),
    path('logout', auth_view.LogoutView.as_view(next_page='study:login'), name='logout'),
    path('room/browse-topics/', views.BrowseTopics.as_view(), name='browse_topics'),
    path('profile/<int:user_id>/', views.ProfileView.as_view(), name='profile'),
    path('room/create/', views.CreateRoomView.as_view(), name='create_room'),
    path('message/<pk>/delete', views.DeleteCommentView.as_view(), name='delete_message'),
    path('profile/<int:pk>/update', views.UpdateProfile.as_view(), name='update_profile'),
]
