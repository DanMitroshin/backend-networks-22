import json
from difflib import SequenceMatcher

from django.shortcuts import get_object_or_404

from Content.models import TrainerBlock


def is_valid_reason_and_argument_answer(question, answer, exclude_ids_array=None, border_ratio=0.5):
    if exclude_ids_array is None:
        exclude_ids_array = []
    # try:
    #     print(question.answers)
    if type(question) == int:
        question = get_object_or_404(TrainerBlock, id=question)
    valid_answers = json.loads(question.valid_answers)
    # except Exception as e:
    #     print("Err", e)
    # print("VALID", valid_answers)
    answer = answer.strip().lower()
    is_valid = False
    best_ratio = 0.0
    match_phrase = ""
    for valid_answer in valid_answers:  # filter(lambda x: x['id'] not in exclude_ids_array, valid_answers):
        right_phrases = valid_answer['ans']
        id_phrase = valid_answer['id']
        is_copy = id_phrase in exclude_ids_array
        potential_match = right_phrases[0]
        for phrase in right_phrases:
            try:
                matcher.set_seq2(phrase)
            except:
                matcher = SequenceMatcher(None, answer, phrase)
            upper_bound_ratio = matcher.real_quick_ratio()
            print(upper_bound_ratio)
            if upper_bound_ratio > border_ratio:
                ratio = matcher.ratio()
                if ratio > border_ratio:
                    return True, ratio, potential_match, id_phrase, is_copy
                    # best_ratio = ratio
                    # match_phrase = potential_match
    return False, 0.0, "", -1, False
