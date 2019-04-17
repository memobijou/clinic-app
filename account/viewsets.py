from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from account.serializers import UserSerializer, SubjectAreaAssignmentSerializer, UserPasswordSerializer, \
    DeviceTokenSerializer


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

    @action(detail=False, methods=['POST'])
    def login(self, request):
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        user = get_object_or_404(User, username=username)
        is_valid_password = user.check_password(password)

        if is_valid_password is True:
            user_serializer = UserSerializer(instance=user)
            return Response(user_serializer.data)
        else:
            return Response({"error": "invalid password or username"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def registration(self, request):
        username = self.request.data.get("username")

        user_already_exists = User.objects.filter(username=username).exists()

        if user_already_exists:
            return Response({"error": "that user already exists"}, status=status.HTTP_400_BAD_REQUEST)
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
        print(f"ABCABCABC::::")
        user_instance = self.get_object()
        profile_instance = user_instance.profile
        serializer = DeviceTokenSerializer(instance=profile_instance, data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            print(f"SHANZE: {instance.pk} - {instance.device_token}")
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
