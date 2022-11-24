import re
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from Content.models import TrainerBlock
from Content.serializers import CheckerTrainerBlockSerializer, TrainerBlockLogCreateSerializer
from Content.constants import QUESTION_TYPES
from Content.utils.answers_checking import is_valid_reason_and_argument_answer
from Statistics.models import TrainerBlockLog, TrainerBlockProgress


class CheckAnswerResult:
    def __init__(self, is_valid, points, meta_info=None):
        self.is_valid = is_valid
        self.points = points
        self.completed = is_valid
        self.meta_info = {} if meta_info is None else meta_info

    def __str__(self):
        return f"ANS: valid: {self.is_valid}, points: {self.points}"


class QuestionCheckerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    valid_answers = serializers.JSONField(required=True)
    question_type = serializers.CharField(required=True, max_length=20)


class AnswerQuestionCheckTemplateSerializer(serializers.Serializer):
    answer = serializers.CharField(required=True, max_length=1000)
    question = QuestionCheckerSerializer()
    calculate_points = serializers.BooleanField(required=False, default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_answer_meta = {}

    def is_valid_user_answer(self, validated_data):
        answer = validated_data["answer"]
        valid_answers = validated_data['question']['valid_answers']
        return answer in valid_answers

    def get_points_for_answer(self, validated_data, is_valid):
        return 1 if is_valid else 0

    def create(self, validated_data):
        is_valid = self.is_valid_user_answer(validated_data)
        if validated_data['calculate_points']:
            points = self.get_points_for_answer(validated_data, is_valid)
        else:
            points = 0

        return CheckAnswerResult(is_valid, points, self.check_answer_meta)


class OneAnswerQuestionCheckSerializer(AnswerQuestionCheckTemplateSerializer):
    pass


def normalize_answer(s):
    return re.sub(r'\s', '', s.lower())


class ManuallyQuestionCheckSerializer(AnswerQuestionCheckTemplateSerializer):

    def is_valid_user_answer(self, validated_data):
        answer = normalize_answer(validated_data["answer"])
        valid_answers = list(map(normalize_answer, validated_data['question']['valid_answers']))
        return answer in valid_answers

    def get_points_for_answer(self, validated_data, is_valid):
        return 3 if is_valid else 0


class RelationsQuestionCheckSerializer(AnswerQuestionCheckTemplateSerializer):

    def get_points_for_answer(self, validated_data, is_valid):
        points = 0
        answer = validated_data["answer"]
        valid_answers = validated_data['question']['valid_answers']
        if is_valid:
            points += 3
        else:
            val = valid_answers[0]
            if len(answer) == len(val):
                p = 0.0
                for a, v in zip(list(answer), list(val)):
                    p += 1.0 if a == v else -0.5
                points += min(max(int(p), 0), 1)
        return points


class ChronologicalQuestionCheckSerializer(AnswerQuestionCheckTemplateSerializer):

    def get_points_for_answer(self, validated_data, is_valid):
        points = 0
        answer = validated_data["answer"]
        valid_answers = validated_data['question']['valid_answers']
        if is_valid:
            points += 3
        else:
            val = valid_answers[0]
            if len(answer) == len(val):
                p = 0.0
                for a, v in zip(list(answer), list(val)):
                    p += 1.0 if a == v else -0.5
                points += min(max(int(p), 0), 1)
        return points


class ManyAnswersQuestionCheckSerializer(AnswerQuestionCheckTemplateSerializer):
    answer = serializers.ListField(child=serializers.CharField(max_length=1000), required=True)

    def is_valid_user_answer(self, validated_data):
        # print("IN VALIDATION")
        answer = validated_data["answer"]
        valid_answers = validated_data['question']['valid_answers']
        is_valid = len(answer) == len(valid_answers)
        if is_valid:
            for v in valid_answers:
                local = False
                for a in answer:
                    if a == v:
                        local = True
                        break
                if not local:
                    is_valid = False
                    break
        return is_valid

class AnswerField(serializers.Field):
    """
    Answer field
    """
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class ReasonsAndArgumentsQuestionCheckSerializer(AnswerQuestionCheckTemplateSerializer):
    answer = AnswerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.argument_answers_queryset = []

    def is_valid_user_answer(self, validated_data):
        answer = validated_data["answer"]
        # alert_message(
        #     f"'Answer:' {answer}, type: {type(answer)}"
        # )
        question_id = validated_data['question']['id']
        user = validated_data["user"]

        is_valid = False
        if not answer:
            return is_valid

        single_answer = self.context.get("single_answer", False)

        if not single_answer:
            # IT MEANS THAT USER HAS ALREADY ANSWERED THIS QUESTION DURING THE TEST
            # SO WE GET ANSWER FROM LOGS
            # alert_message("1")
            argument_answers_queryset = TrainerBlockLog.objects.filter(
                user=user,
                trainer_block__id=question_id,
            )
            self.argument_answers_queryset = argument_answers_queryset
            for argument_answer in argument_answers_queryset.filter(is_valid=True):
                if argument_answer.id in answer:
                    is_valid = True
                    break
                # alert_message("5")
        else:
            is_valid, ratio, match_phrase, id_match, is_copy = is_valid_reason_and_argument_answer(
                question_id,
                answer=answer,
                exclude_ids_array=self.context.get('exclude_ids_array'),
                border_ratio=0.5
            )
            self.check_answer_meta.update({
                'ratio': ratio,
                'match_phrase': match_phrase,
                'id_match': id_match,
                'is_copy': is_copy,
            })

        return is_valid

    def get_points_for_answer(self, validated_data, is_valid):
        points = 0
        answer = validated_data["answer"]
        for log in self.argument_answers_queryset:
            if log.is_valid and log.id in answer:
                points += 5
        return points


QUESTION_CHECK_SERIALIZERS_BY_TYPE = {
    QUESTION_TYPES.ONE_ANSWER: OneAnswerQuestionCheckSerializer,
    'map': OneAnswerQuestionCheckSerializer,
    QUESTION_TYPES.MANUALLY: ManuallyQuestionCheckSerializer,
    QUESTION_TYPES.RELATIONS: RelationsQuestionCheckSerializer,
    QUESTION_TYPES.CHRONOLOGICAL: ChronologicalQuestionCheckSerializer,
    QUESTION_TYPES.MANY_ANSWERS: ManyAnswersQuestionCheckSerializer,
    QUESTION_TYPES.REASONS_AND_ARGUMENTS: ReasonsAndArgumentsQuestionCheckSerializer,
}


class TrainerBlockCheckAnswerSerializer(serializers.Serializer):
    answer = AnswerField(required=True)
    id = serializers.IntegerField(required=True)

    # def validate_answer(self, value):
    #     # print("Validate answer:", value)
    #     # if 'answer' not in value.keys():
    #     #     raise serializers.ValidationError("User answer (ans) does not exists [answer]")
    #     # if 'id' not in value.keys():
    #     #     raise serializers.ValidationError("Question id does not exists [answer]")
    #     # value['answer'] = value.pop('ans')
    #     return value

    def create(self, validated_data):

        single_answer = self.context.get("single_answer", False)

        question = get_object_or_404(TrainerBlock, id=validated_data['id'])
        serializer_class = QUESTION_CHECK_SERIALIZERS_BY_TYPE[question.question_type]

        data = {
            'answer': validated_data["answer"],
            "question": CheckerTrainerBlockSerializer(question).data,
            "calculate_points": validated_data["calculate_points"]
        }
        # print("Data:", data)
        # print("SER:", serializer_class)
        # print("User:", validated_data["user"])
        user = validated_data["user"]
        serializer = serializer_class(data=data, context=self.context)
        serializer.is_valid(raise_exception=True)
        checker_info: CheckAnswerResult = serializer.save(user=user)

        def get_str_answer(answer):
            try:
                return str(answer)[:100]
            except:
                return ""

        if single_answer or question.question_type != QUESTION_TYPES.REASONS_AND_ARGUMENTS:
            log_serializer = TrainerBlockLogCreateSerializer(data={
                'user': user.id,
                'trainer_block': question.id,
                'is_valid': checker_info.is_valid,
                'answer': get_str_answer(data['answer']),
            })
            log_serializer.is_valid(raise_exception=True)
            trainer_block_log = log_serializer.save()
            checker_info.meta_info.update({'trainer_block_log_id': trainer_block_log.id})

        trainer_block_progress, _ = TrainerBlockProgress.objects.get_or_create(
            trainer_block=question,
            user=user
        )
        trainer_block_progress.add_answer(checker_info.is_valid)
        if trainer_block_progress.successful_attempts > 0:
            checker_info.completed = True
        return checker_info
