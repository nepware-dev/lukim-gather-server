from lukimgather.serializers import UserModelSerializer
from user.models import Grant


class GrantSerializer(UserModelSerializer):
    class Meta:
        model = Grant
        fields = "__all__"
