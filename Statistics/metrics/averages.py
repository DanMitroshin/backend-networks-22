from datetime import timedelta

from .utils import aggregate
from Statistics.models import ProductLog, ProductProgress, TrainerBlockProgress


def average_progress_per_product():
    queryset = ProductProgress.objects.all().prefetch_related('product')
    values = [
        {
            'product': f'{item.product.name} ({item.product.id})',
            'progress': item.progress
        } for item in queryset if item.product.lesson_type == 'p2'
    ]
    return aggregate(
        values,
        lambda x: sum(x) / len(x),
        'progress',
        group_by='product',
    )


def average_solved_percentage_per_product():
    queryset = ProductLog.objects.all().prefetch_related('product')
    values = [
        {
            'product': f'{item.product.name} ({item.product.id})',
            'solved_percentage': item.solved_percentage
        } for item in queryset if item.product.lesson_type == 'p2'
    ]
    return aggregate(
        values,
        lambda x: sum(x) / len(x),
        'solved_percentage',
        group_by='product',
    )


def average_duration_per_product():
    queryset = ProductLog.objects.filter(time_to_complete__gt=timedelta(0)).prefetch_related('product')
    values = [
        {
            'product': f'{item.product.name} ({item.product.id})',
            'total_seconds': item.time_to_complete.total_seconds()
        } for item in queryset if item.product.lesson_type == 'p2'
    ]
    print([(elem.product.lesson_type, str(elem.time_to_complete))for elem in queryset])
    return aggregate(
        values,
        lambda x: sum(x) / len(x),
        'total_seconds',
        group_by='product',
    )


def average_success_rate_per_trainer_block(section='__all__'):
    queryset = (
        TrainerBlockProgress.objects.filter(attempts__gt=0)
        .prefetch_related('trainer_block', 'trainer_block__tags')
    )
    values = []
    for item in queryset:
        for tag in item.trainer_block.tags.all():
            values.append({
                'tag': tag.description,
                'success_rate': item.success_rate
            })

    result = aggregate(
        values,
        lambda x: int(10000 * sum(x) / len(x)) / 100,
        'success_rate',
        group_by='tag',
    )
    result.sort(key=lambda x: x['value'])
    return result
