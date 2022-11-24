from django.http import Http404

from .averages import average_progress_per_product
from .averages import average_solved_percentage_per_product
from .averages import average_success_rate_per_trainer_block
from .averages import average_duration_per_product

from .retention import retention

from .totals import total_product_completes_per_day
from .totals import total_product_completes_per_user
from .totals import total_user_completes_per_day
from .totals import total_inits_per_day
from .totals import total_unique_users_from_init_per_day

metrics = (
    {
        'func': average_duration_per_product,
        'selectors': [],
        'human': {
            'name': 'Average duration per product',
            'grouped_by': 'Product name (id)',
            'metric': 'Average duration (seconds)'
        },
    },
    {
        'func': average_progress_per_product,
        'selectors': [],
        'human': {
            'name': 'Average progress per product',
            'grouped_by': 'Product name (id)',
            'metric': 'Average duration (seconds)'
        },
    },
    {
        'func': average_success_rate_per_trainer_block,
        'selectors': [
            {
                'name': 'section',
                'title': 'Section',
                'options' : [
                    {'name': 'All sections', 'value': '__all__'},
                    {'name': 'Ancient history', 'value': 'anc'},
                    {'name': 'Renaissance', 'value': 'ren'},
                    {'name': 'Modernity', 'value': 'mod'},
                ]
            }
        ],
        'human': {
            'name': 'Average success rate per trainer block',
            'grouped_by': 'Tag',
            'metric': 'Success_rate (%)'
        },
    },
    {
        'func': retention,
        'selectors': [],
        'human': {
            'name': 'Retention rate',
            'grouped_by': 'Days from registration',
            'metric': 'Retention'
        },
    },
    {
        'func': total_product_completes_per_day,
        'selectors': [],
        'human': {
            'name': 'Total products completed per day',
            'grouped_by': 'Date',
            'metric': 'Total completed products'
        },
    },
    {
        'func': total_product_completes_per_user,
        'selectors': [],
        'human': {
            'name': 'Total products completed per user',
            'grouped_by': 'User',
            'metric': 'Total completed products'
        },
    },
    {
        'func': total_user_completes_per_day,
        'selectors': [],
        'human': {
            'name': 'Total users completed per day',
            'grouped_by': 'Date',
            'metric': 'Unique users'
        },
    },
    {
        'func': total_unique_users_from_init_per_day,
        'selectors': [],
        'human': {
            'name': 'Unique users entered in app',
            'grouped_by': 'Date',
            'metric': 'Unique users'
        },
    },
    {
        'func': total_inits_per_day,
        'selectors': [],
        'human': {
            'name': 'Total enters per day',
            'grouped_by': 'Date',
            'metric': 'Total enters'
        },
    },
)


for metric in metrics:
    metric['value'] = metric['func'].__name__


def get_metric(value):
    for metric in metrics:
        if metric['value'] == value:
            return metric
    raise Http404()
