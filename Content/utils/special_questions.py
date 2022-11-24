import json
from django.shortcuts import get_object_or_404

from Content.models import TrainerBlock, SpecialQuestionAnswer


def save_special_answers(user, answers):
    for answer in answers:
        # print("IN ANSWERS")
        try:
            question = get_object_or_404(TrainerBlock, id=answer['id'])
            answer_user = answer['ans']
            if question.question_type == 'many':
                answer_str = str(json.dumps(answer_user))
                SpecialQuestionAnswer.objects.create(
                    user=user,
                    question=question,
                    answer=answer_str
                )
            elif question.question_type in ["one", 'self']:
                SpecialQuestionAnswer.objects.create(
                    user=user,
                    question=question,
                    answer=answer_user
                )

        except:
            continue


def get_special_questions_and_indexes_for_user(user):
    return [], []

