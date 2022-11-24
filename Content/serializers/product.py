import datetime
import json
import random

from rest_framework import serializers

from Content.models import (
    Product,
    MediaBlock,
    TrainerBlock,
    TrainerBlockTag,
    ContentTheme)
from Content.constants import GENERATED_PRODUCT_TYPES, BASE_LESSON_TYPE_CHOICE, QUESTION_TYPES
from Content.utils.special_questions import get_special_questions_and_indexes_for_user
from Statistics.models import ProductLog, TrainerBlockLog, ProductProgress


class TrainerBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerBlock
        exclude = ['valid_answers', 'answers']
        read_only = True

    def to_representation(self, instance):

        data = super().to_representation(instance)
        valid_answers = json.loads(instance.valid_answers)
        has_content_access = self.context.get('has_content_access', False)

        data['question_type'] = QUESTION_TYPES.ONE_ANSWER if data['question_type'] == 'map' else data['question_type']
        if data['question_type'] == QUESTION_TYPES.ONE_ANSWER:
            invalid_answers = json.loads(instance.invalid_answers)
            data['valid_answers'] = [random.choice(valid_answers)]
            data['answers'] = data['valid_answers'] + random.sample(invalid_answers,
                                                                    k=min(3, len(invalid_answers)))
            random.shuffle(data['answers'])
        elif data['question_type'] == QUESTION_TYPES.REASONS_AND_ARGUMENTS:
            answers = json.loads(instance.answers)
            data['valid_answers'] = valid_answers if has_content_access else []
            data['answers'] = answers
        else:
            answers = json.loads(instance.answers)
            data['valid_answers'] = valid_answers
            data['answers'] = answers
        try:
            data['img'] = json.loads(data['img'])
        except ValueError:
            pass
        return data


class CheckerTrainerBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerBlock
        fields = ['valid_answers', 'question_type', 'id']
        read_only = True

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['valid_answers'] = json.loads(instance.valid_answers)
        return data


class ProductLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLog
        fields = ('user', 'product', 'completed', 'time_to_complete')


class TrainerBlockLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerBlockLog
        fields = '__all__'

    def validate_answer(self, value):
        # print("VALIDATE~!!!!!!!!!!!!!!!1 ANSWER")
        return str(value)[:TrainerBlockLog._meta.get_field('answer').max_length]


class MediaBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaBlock
        fields = '__all__'
        read_only = True


class TrainerProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['media_blocks', 'trainer_blocks']
        read_only = True

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        questions = []
        has_content_access = self.context.get('has_content_access', False)

        for trainer_block in instance.trainer_blocks.all().order_by('?'):
            trainer_serializer = TrainerBlockSerializer(trainer_block, context={
                'has_content_access': has_content_access
            })
            data = trainer_serializer.data
            questions.append(data)

        serializer['questions'] = questions

        if 'user' in self.context.keys():
            serializer['specialQuestions'], serializer['specialQuestionsIndexes'] = \
                get_special_questions_and_indexes_for_user(self.context['user'])
        return serializer


class ProductPreOpenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        read_only = True
        fields = ['id', 'index', 'name', 'lesson_type', 'tag']

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        user = self.context.get('user', None)
        progress = 0

        if user is not None:
            product_progress = ProductProgress.objects.filter(user=user, product=instance)
            if product_progress.exists():
                progress = product_progress.first().progress

        serializer['progress'] = progress
        return serializer


class ContentThemeMainInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentTheme
        read_only = True
        fields = ['id', 'index', 'name']

    def get_item_from_context(self, item, default=None):
        try:
            return self.context.get(item, default)
        except:
            return default

    def to_representation(self, instance):
        context = self.context
        user = self.get_item_from_context('user')
        products_filter = self.get_item_from_context("products_filter", {})

        serializer = super().to_representation(instance)
        if instance.video:
            serializer['videoId'] = instance.video.index

        theme_products = Product.objects \
            .filter(active__gt=0, content_theme=instance) \
            .filter(**products_filter) \
            .order_by('index')

        lessons = []
        for pr in theme_products:
            lessons.append(ProductPreOpenSerializer(pr, context={'user': user}).data)
        serializer['lessons'] = lessons  # sorted(lessons, key=lambda a: a['index'])
        return serializer


class MediaProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = [
            'media_blocks',
            'trainer_blocks',
            'access_groups',
            'tag',
        ]
        read_only = True

    def to_representation(self, instance):
        # print("INST:", instance)
        serializer = super().to_representation(instance)
        blocks = []
        for media_block in instance.media_blocks.all().order_by('id'):
            media_serializer = MediaBlockSerializer(media_block)
            blocks.append(media_serializer.data)

        # print("BLOCKS:", list(map(lambda x: x['id'], blocks)))
        # s = sorted(blocks, key=lambda x: x['id'])
        # print("NEED:", list(map(lambda x: x['id'], s)))  # blocks)
        serializer['blocks'] = blocks

        return serializer


class ProductPostSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    time = serializers.IntegerField(min_value=0, required=False, default=0)


class TrainerProductPostSerializer(ProductPostSerializer):
    answers = serializers.JSONField()


class TrainerBlocksPostSerializer(serializers.Serializer):
    answers = serializers.JSONField()
    time = serializers.IntegerField(min_value=0, required=False, default=0)


class LessonGetSerializer(serializers.Serializer):
    class LessonGetParams:
        def __init__(self, lesson_type, lesson):
            self.lesson_type = lesson_type
            self.lesson = lesson

        def __str__(self):
            return f"{self.lesson_type}, lesson id{self.lesson}"

    lesson_type = serializers.ChoiceField(
        choices=BASE_LESSON_TYPE_CHOICE,
        required=True,
    )
    lesson = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return self.LessonGetParams(**validated_data)


class MediaProductPostSerializer(ProductPostSerializer):
    last_block = serializers.IntegerField()


class ProductListGetSerializer(serializers.Serializer):
    section = serializers.CharField(max_length=250, required=False)
    lesson_type = serializers.ChoiceField(
        choices=BASE_LESSON_TYPE_CHOICE,
        required=False
    )

    def validate_section(self, value):
        if Product.objects.filter(section__exact=value).exists():
            return value
        raise serializers.ValidationError("Section does not exists")


class TrainerProductCreateRetrieveSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[
        (GENERATED_PRODUCT_TYPES.PERSONAL, 'Generated with the most difficult questions for user'),
        (GENERATED_PRODUCT_TYPES.RANDOM, 'Generated randomly')],
        default=GENERATED_PRODUCT_TYPES.PERSONAL)
    tag = serializers.CharField(max_length=5, default='')
    amount = serializers.IntegerField(default=25)
    section = serializers.CharField(default='')

    def validate_tag(self, value):
        if TrainerBlockTag.objects.filter(tag=value).exists() or value == '':
            return value
        raise serializers.ValidationError("Tag does not exists [tag]")

    def validate_amount(self, value):
        if 3 <= value <= 50:
            return value
        raise serializers.ValidationError("Amount must be in range (3, 50), but got [amount]")

    def validate_section(self, value):
        if TrainerBlock.objects.filter(section__exact=value).exists():
            return value
        elif value == '' or value == '__all__':
            return ''
        raise serializers.ValidationError("Section does not exists [section]")

    def validate(self, attrs):
        attrs['product_type'] = attrs.pop('type')
        return attrs
