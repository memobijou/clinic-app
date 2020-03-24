from django.db.models import Q, F, Sum
from django.db.models.functions import Coalesce
from rest_framework import serializers
from django.urls import reverse, reverse_lazy
from filestorage.utils import send_push_notifications
from filestorage.models import File, FileDirectory
from decimal import Decimal
from django.contrib.auth.models import User
from filestorage.models import FileUserHistory
from django.db import transaction


@transaction.atomic
def send_file_messages_through_firebase(file, is_new=True):
    if file.parent_directory.announcement is True:
        if is_new is True:
            title = f"Neue Datei in {file.parent_directory.name}"
            message = f'"{file.file.name}" Version {file.version_with_point}'
        else:
            title = f"Update vorhanden in {file.parent_directory.name}"
            message = f"{file.file.name} jetzt auf Version {file.version_with_point}"

        send_push_notifications(User.objects.all(), title, message, "filestorage")
        users_without_history = User.objects.filter(~Q(fileuserhistory__file=file)).distinct()
        bulk_instances = []
        for user in users_without_history:
            bulk_instances.append(FileUserHistory(user=user, file=file))
        # print(getattr(FileUserHistory.objects.filter(file=file).first(), "unread_notifications", "0"))

        FileUserHistory.objects.bulk_create(bulk_instances)
        FileUserHistory.objects.filter(file=file).update(
            unread_notifications=F("unread_notifications") + 1)

        # print(getattr(FileUserHistory.objects.filter(file=file).first(), "unread_notifications", "0"))
        # print(getattr(FileUserHistory.objects.filter(file=file).first(), "user", "NO USER !!"))


class FileSerializerBase(serializers.ModelSerializer):
    type = serializers.StringRelatedField()
    filename = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()

    def get_filename(self, instance: File):
        return instance.filename()

    def get_file(self, instance):
        request = self.context.get("request")
        if request.is_secure():
            scheme = "https"
        else:
            scheme = "http"
        file_url = f'{str(scheme)}://{str(request.get_host())}' \
            f'{reverse_lazy("api_filestorage:files", kwargs={"pk": instance.pk})}'
        return file_url

    class Meta:
        model = File
        fields = ("file", "parent_directory", "type", "pk", "version", "filename")

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        send_file_messages_through_firebase(instance)
        return instance


class FileSerializer(FileSerializerBase):
    pass


class FileUpdateSerializer(FileSerializerBase):
    def validate_version(self, value):
        print(f"version 1: {type(value)}")
        print(f"version 2: {value}")
        if type(value) not in [float, int, Decimal]:
            raise serializers.ValidationError(f"Sie müssen eine Zahl eingeben")
        if value <= self.instance.version:
            raise serializers.ValidationError(f"Version muss größer als {self.instance.version} sein")
        return value


class FileDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FileDirectory
        fields = ("pk", "name", "type", "files", "child_directories", "parent", "unread_notifications",)

    files = FileSerializer(many=True)
    child_directories = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    unread_notifications = serializers.SerializerMethodField()

    def get_unread_notifications(self, instance):
        user_id = self.context.get("user_id")
        directory_hierarchy = [instance.pk]
        self.get_directory_hierarchy(directory_hierarchy, directory_hierarchy)
        print(f'flutter: {directory_hierarchy}')
        return FileUserHistory.objects.filter(
            user_id=user_id, file__parent_directory_id__in=directory_hierarchy).aggregate(total=Coalesce(
                Sum("unread_notifications"), 0)).get("total")

    def get_directory_hierarchy(self, directories, directory_hierarchy):
        new_directories = []
        for directory in FileDirectory.objects.filter(parent_id__in=directories):
            new_directories.append(directory.id)
            directory_hierarchy.append(directory.id)
        if len(new_directories) == 0:
            return
        self.get_directory_hierarchy(new_directories, directory_hierarchy)

    def get_child_directories(self, value):
        child_directories_queryset = value.child_directories.values("name", "pk")
        for child_directory in child_directories_queryset:
            request = self.context.get("request")
            user_id = self.context.get("user_id")
            print(f"heyyy: {request}")

            if user_id:
                url = reverse("api_filestorage:directories-detail", kwargs={"pk": child_directory.get("pk"),
                                                                            "user_id": user_id})
            else:
                url = reverse("filestorage:directories-detail", kwargs={"pk": child_directory.get("pk")})
            if request:
                child_directory["link"] = request.build_absolute_uri(url)
            else:
                child_directory["link"] = url

            directory_hierarchy = [child_directory.get("pk")]
            self.get_directory_hierarchy(directory_hierarchy, directory_hierarchy)
            print(f'flutter: {directory_hierarchy}')
            child_directory["unread_notifications"] = FileUserHistory.objects.filter(
                user_id=user_id, file__parent_directory_id__in=directory_hierarchy).aggregate(total=Coalesce(
                    Sum("unread_notifications"), 0)).get("total")
        result = child_directories_queryset
        return result

    def get_parent(self, value):
        if value.parent:
            request = self.context.get("request")
            user_id = self.context.get("user_id")
            url = reverse("api_filestorage:directories-detail", kwargs={"pk": value.parent.pk, "user_id": user_id})
            parent_dict = {"name": value.parent.name, "pk": value.parent.id}
            if request:
                parent_dict["link"] = request.build_absolute_uri(url)
            else:
                parent_dict["link"] = url
            result = parent_dict
            return result

    def save(self, **kwargs):
        super().save(**kwargs)
