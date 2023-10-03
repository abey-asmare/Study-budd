from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views import View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import CreateUser, CommentForm, CreateRoomForm, UpdateProfileForm
from .models import UserProfile, Topic, Room, Message
from urllib.parse import unquote
from django.utils.html import escape
from django.contrib.auth.models import User


# we can do it like this, or we can define another view (for the rest like routing) and another url
# like: this/param/ and we have to pass the parameter in the url to the function/class in the views.
# class HomeFilterView(LoginRequiredMixin, View):
#     login_url = reverse_lazy('study:login')
#     model = Room
#     template_name = 'home/index.html'
#
#     def get(self, request, filter):
#         rooms = self.model.objects.filter(
#             Q(topic__name__icontains=filter) |
#             Q(name__icontains=filter) |
#             Q(host__username__icontains=filter)
#         )
#         topics = Topic.objects.all()
#         messages = Message.objects.filter(room__in=rooms).all()
#         context = {'room_list': rooms, 'topics': topics, 'messages': messages}
#         return render(request, self.template_name, context)
# in this case we may have some special characters like # in c# # is called fragment identifier, the browser
# will not send anything after it. so to bypass it we have to encode using urlencode filter in out template
# and decode it in our backend also we have to escape it to prevent xss atacks

class HomeView(LoginRequiredMixin, View):
    model = Room
    template_name = 'home/index.html'

    def get(self, request):
        q = escape(unquote(self.request.GET.get('q'))) if request.GET.get('q') else ''
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(host__username__icontains=q)
        )
        topics = Topic.objects.all()
        messages = Message.objects.filter(room__in=rooms)
        context = {'room_list': rooms, 'messages': messages, 'topics': topics}
        return render(request, self.template_name, context)


class SignUp(SuccessMessageMixin, CreateView):
    form_class = CreateUser
    success_url = reverse_lazy('study:login')
    template_name = 'home/signup.html'
    success_message = "%(username)s was created successfully"


class BrowseTopics(LoginRequiredMixin, View):
    model = Topic
    template_name = 'home/topics.html'

    def get(self, request):
        q = escape(unquote(self.request.GET.get('q'))) if request.GET.get('q') else ''
        context = {'topic_list': self.model.objects.filter(Q(name__icontains=q))}
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    template_name = 'home/profile.html'

    def get(self, request, user_id):
        context = {
            'profile': get_object_or_404(UserProfile, user=user_id),
            'topics': Topic.objects.all(),
            'rooms': Room.objects.filter(host=user_id),
            'messages': Message.objects.filter(user_id=user_id),
        }
        return render(request, self.template_name, context)


class CreateRoomView(LoginRequiredMixin, View):
    template_name = 'home/create-room.html'

    def get(self, request):
        context = {'form': CreateRoomForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        topic_id = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(id=topic_id)
        print(topic)
        room, is_created = Room.objects.get_or_create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        room.participants.add(request.user)
        return redirect(reverse_lazy('study:home'))


class RoomDetailView(LoginRequiredMixin, View):
    model = Room

    def get(self, request, pk):
        context = {
            'room': get_object_or_404(self.model, pk=pk),
            'form': CommentForm(),
        }
        return render(request, 'home/room.html', context)

    def post(self, request, pk):
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.room_id = pk
            form.save()
            return redirect(reverse_lazy('study:room', kwargs={'pk': pk}))
        return self.get(request, pk)


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('study:home')
    template_name = 'home/delete-comment.html'

    def test_func(self):
        message = self.get_object()
        return True if message.user == self.request.user else False


class UpdateProfile(LoginRequiredMixin, View):
    model = UserProfile
    template_name = 'home/edit-user.html'

    def get(self, request, pk):
        profile = get_object_or_404(self.model, pk=pk, user=request.user)
        form = UpdateProfileForm(
            initial={
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'username': profile.user.username,
                'email': profile.user.email,
                'about': profile.about
            })
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk)
        form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('study:profile', kwargs={'user_id': profile.user.id}))

        context = {'form': form}
        return render(request, self.template_name, context)