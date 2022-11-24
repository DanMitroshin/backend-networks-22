import datetime
from rest_framework import serializers

from Content.utils import strip_dict_values
from Statistics.models import UserAnswerForReview


class UserAnswerForReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswerForReview
        exclude = ('id', 'user', 'timestamp')

    def to_internal_value(self, data):
        # data['user'] = self.context['user'].id
        data['question'] = data["id"]
        data['timestamp'] = datetime.datetime.utcnow()
        data = strip_dict_values(data)

        return super().to_internal_value(data)
