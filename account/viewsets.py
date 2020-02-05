from django.contrib.auth.models import User
from django.db.models import Q
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import mixins
from account.serializers import UserSerializer, SubjectAreaAssignmentSerializer, UserPasswordSerializer, \
    DeviceTokenSerializer, ProfileEditionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        print(self.request.POST)
        self.filter_by_pk()
        return self.queryset

    def filter_by_pk(self):
        pk_filter_value = self.request.GET.get("pk")
        if pk_filter_value is not None and pk_filter_value != "":
            self.queryset = self.queryset.filter(pk=pk_filter_value)

    @action(detail=False, methods=['POST'], authentication_classes=[], permission_classes=[])
    def login(self, request):
        email = self.request.POST.get("email")
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        if email:
            user = get_object_or_404(User, email__iexact=email)
        else:
            user = get_object_or_404(User, username=username)

        is_valid_password = user.check_password(password)

        if is_valid_password is True:
            user_serializer = UserSerializer(instance=user)
            return Response(user_serializer.data)
        else:
            return Response({"error": "Benutzername oder Passwort falsch"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], authentication_classes=[], permission_classes=[])
    def registration(self, request):
        username = self.request.data.get("username")
        email = self.request.data.get("email")

        user_already_exists = User.objects.filter(Q(Q(username=username) | Q(email=email))).exists()

        if user_already_exists:
            return Response({"error": "Dieser Benutzer existiert bereits"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = UserPasswordSerializer(data=self.request.data)
            if serializer.is_valid():
                instance = serializer.save()
                data = serializer.data
                data.pop("password")
                data.pop("password2")
                data = {**data, "pk": instance.pk}
                return Response(data)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PUT"], url_path="subject-area-assignment")
    def subject_area_assignment(self, request, pk=None):
        user_instance = self.get_object()
        profile_instance = user_instance.profile
        serializer = SubjectAreaAssignmentSerializer(instance=profile_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PUT"], url_path="device-token-assignment")
    def device_token_assignment(self, request, pk=None):
        user_instance = self.get_object()
        profile_instance = user_instance.profile
        serializer = DeviceTokenSerializer(instance=profile_instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @atomic
    @action(detail=True, methods=["PUT"], url_path="profile-edition")
    def profile_edition(self, request, pk=None):
        user_instance = self.get_object()
        profile_instance = user_instance.profile
        print(f"whaaat: {profile_instance.title}")
        serializer = ProfileEditionSerializer(instance=profile_instance, data=request.data)
        first_name = serializer.initial_data.pop("first_name")
        last_name = serializer.initial_data.pop("last_name")

        initial_title = profile_instance.title

        if not serializer.initial_data.get("title"):
            serializer.initial_data["title"] = initial_title

        if first_name:
            first_name = first_name[0]

        if last_name:
            last_name = last_name[0]

        if serializer.is_valid():
            instance = serializer.save()
            user = instance.user
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if first_name and last_name:
                user.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationLoginViewset(viewsets.ModelViewSet):
    pass
