from lukimgather.serializers import UserModelSerializer
from project.models import Project


class ProjectSerializer(UserModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
        ]
