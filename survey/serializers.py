from lukimgather.serializers import UserModelSerializer
from survey.models import Form, Survey


class FormSerializer(UserModelSerializer):
    class Meta:
        model = Form
        field = "__all__"


class SurveySerializer(UserModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"
