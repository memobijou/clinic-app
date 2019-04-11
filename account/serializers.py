from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from account.models import Profile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from subject_area.models import SubjectArea
from subject_area.serializers import SubjectAreaSerializer


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", )


class BasicProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = Profile
        fields = ("is_admin", "user", )


class ProfileSerializer(serializers.ModelSerializer):
    mentor = BasicUserSerializer(read_only=True)
    subject_area = SubjectAreaSerializer(read_only=True)
    subject_area_id = serializers.ChoiceField(
        source="subject_area.pk", allow_null=True, label="Fachrichtung (subject_area_id)", choices=())

    class Meta:
        model = Profile
        fields = ("is_admin", "mentor", "device_token", "subject_area", "subject_area_id", )
        read_only_fields = ('is_admin',)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    students = BasicProfileSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", "profile", "students", )

    def update(self, instance, validated_data):
        profile = validated_data.pop("profile")
        subject_area = profile.pop("subject_area")
        User.objects.filter(pk=instance.pk).update(**validated_data)
        Profile.objects.filter(pk=instance.profile.pk).update(**profile, subject_area_id=subject_area.get("pk"))
        instance.refresh_from_db()
        return instance


class SubjectAreaAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("subject_area",)


# ViewSets define the view behavior.
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

    @action(detail=True, methods=["PUT"], url_path="subject-area-assignment")
    def subject_area_assignment(self, request, pk=None):
        print(f"ahd wenn: {pk}")
        user_instance = self.get_object()
        profile_instance = user_instance.profile
        serializer = SubjectAreaAssignmentSerializer(instance=profile_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
