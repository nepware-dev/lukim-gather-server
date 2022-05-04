from lukimgather.serializers import UserModelSerializer
from survey.models import Form, Survey, SurveyAnswer


class FormSerializer(UserModelSerializer):
    class Meta:
        model = Form
        field = "__al__"


class SurveySerializer(UserModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"


class SurveyAnswerSerializer(UserModelSerializer):
    class Meta:
        model = SurveyAnswer
        fields = "__all__"


class WritableSurveyAnswerSerializer(SurveyAnswerSerializer):
    class Meta:
        model = SurveyAnswer
        exclude = ("survey",)
