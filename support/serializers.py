from lukimgather.serializers import UserModelSerializer
from support.models import Feedback


class FeedbackSerializer(UserModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
