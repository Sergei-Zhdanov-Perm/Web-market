import json
import os

from django.conf import settings
from django.http.request import HttpRequest
from django.contrib.auth import logout, login, authenticate, hashers
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProfileUser
from .serializers import ProfileSerializer
from .forms import ProfileForm


class SignOutAPIView(APIView):

    def post(self, request):
        logout(request)
        return Response(status=200)


class SignInAPIView(APIView):

    def post(self, request: HttpRequest) -> Response:
        data = json.loads(request.body)
        username: str = data["username"]
        password: str = data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(status=200)
        return Response(status=500)


class SignUpAPIView(APIView):

    def post(self, request: HttpRequest) -> Response:
        data = json.loads(request.body)
        username: str = data["username"]
        password: str = data["password"]
        name: str = data["name"]
        email = username + "@django.com"
        user = User.objects.create(username=username, email=email)
        user.password = hashers.make_password(password)
        user.save()
        ProfileUser.objects.create(
            user=user, email=email, avatar="profile/avatar_default.png"
        )

        if user is not None:
            login(request, user)
            return Response(status=200)
        return Response(status=500)


class ProfileUserAPIView(APIView):

    def get(self, request: HttpRequest) -> Response:
        profile = ProfileUser.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)

        return Response(serializer.data)

    def post(self, request: HttpRequest) -> JsonResponse:
        full_name = request.data["fullName"].split()
        surname = full_name[0]
        name = full_name[1]
        patronymic = full_name[2]
        phone = request.data["phone"]

        profile = ProfileUser.objects.get(user=request.user)
        profile.surname = surname
        profile.name = name
        profile.patronymic = patronymic
        profile.phone = phone
        profile.save()

        data = {
            "full_name": f"{profile.surname} {profile.name} {profile.patronymic}",
            "email": profile.email,
            "phone": profile.phone,
            "avatar": {
                "src": profile.avatar.url,
                "alt": profile.avatar.name,
            },
        }

        return JsonResponse(data)


class AvatarChangeAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request: HttpRequest) -> Response:
        user_profile = ProfileUser.objects.get(user=request.user)
        avatar_file = request.FILES.get("avatar")
        avatar_path = os.path.join(settings.MEDIA_ROOT, str(user_profile.avatar))
        if avatar_file:
            if (
                os.path.isfile(avatar_path)
                and user_profile.avatar != "profile/avatar_default.png"
            ):
                os.remove(avatar_path)

        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return Response(status=200)
        return Response(status=500)


class ChangePasswordAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request: HttpRequest) -> Response:
        user = request.user
        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")

        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return Response(status=200)
        return Response(status=500)
