METRIC = 'metric'
UNIQUE_USERS = 'unique_users'
NEW_USERS = 'new_users'
ENTERED_USERS = 'entered_users'
COMPLETED_PRODUCTS = 'completed_products'
USER_COMPLETED = 'user_completed'
UNIQUE_USERS_TIMES = 'unique_users_times'
USERS_TIMES = 'users_times'
CONVERSION = 'conversion'

ACTIVITY = 'activity'
CARDS__RUS = 'cards__rus'
CARDS__WORLD = 'cards__world'
CARDS__TERMS = 'cards__terms'
LIST__RUS = 'list__rus'
LIST__WORLD = 'list__world'
LIST__TERMS = 'list__terms'
CONTENT__PICTURES = 'learn pictures'
CONTENT__MAPS = 'learn maps'
LEARN__LITERATURE = 'learn maps'
LEARN__ARCHITECTURE = 'learn maps'
LEARN__PERSONS = 'learn maps'
LEARN__DATES_RUS = 'learn d_rus'
LEARN__SCULPTURE = 'learn sculpture'
LEARN__TERMS = 'learn terms'
CONTENT__ = 'content__'
CONTENT0__ = 'content0__'
CONTENT1__ = 'content1__'
CONTENT_LIST__ = 'content_list__'
STATISTICS__ = 'statistics__'

VALUE = 'value'
AVERAGE = 'average'
TOTAL_USAGES = 'total_usages'
TIME = 'time'
CARDS_AMOUNT = 'cards_amount'
COMPLETED_BLOCKS = 'completed_blocks'
RIGHT_ANSWERS_AMOUNT = "right_answers_amount"
TOTAL_ANSWERS_AMOUNT = "total_answers_amount"
RATING_REQUEST_AMOUNT = "rating_request_amount"
SUBSCRIPTION_PRICES_REQUEST_AMOUNT = "sub_prices_request_amount"
SUBSCRIPTION_SALES = "subscription_sales"
REVENUE_FROM_SUBSCRIPTIONS = "revenue_from_subscriptions"
CONVERSION_TO_SALE_SUBSCRIPTION = "conversion_to_sale_sub"

ACTIVITY_NAMES = {
    CARDS__RUS: 'exit cards d_rus',
    CARDS__WORLD: 'exit cards d_world',
    CARDS__TERMS: 'exit cards terms',
    LIST__RUS: 'exit rus dates',
    LIST__WORLD: 'exit world dates',
    LIST__TERMS: 'exit terms',
    CONTENT__: "C_CON",
    CONTENT0__: "C_CON0",
    CONTENT1__: "C_CON1",
    CONTENT_LIST__: "C_LIST",
    STATISTICS__: "STAT",
    # LEARN__PICTURES: LEARN__PICTURES,
}


PRODUCT_RATING = 'product_rating'
PRODUCTS = 'products'
THEORY = 'theory'
TESTS = 'tests'
PERSONAL = 'personal'
THEME = 'theme'
ANC = 'anc'
REN = 'ren'
MOD = 'mod'
ALL = 'all'
THEORY__ANC = THEORY + '__' + ANC
THEORY__REN = THEORY + '__' + REN
THEORY__MOD = THEORY + '__' + MOD

PRODUCT_TYPES = {
    ALL: ['p1', 'p2', 'p3'],
    THEORY: ['p1'],
    TESTS: ['p2', 'p3'],
    PERSONAL: ['p3'],
    THEME: ['p2']
}

PRODUCT_RATING_TYPES = {
    THEORY: 'p1',
    TESTS: 'p2',
}

PRODUCT_SECTIONS = {
    ANC: ANC,
    REN: REN,
    MOD: MOD,
    ALL: ''
}

AVERAGE_TIME = 'average_time'
TOTAL_TIME = 'total_time'
# TOTAL_USAGES
AVERAGE_COMPLETED_BLOCKS = 'average_completed_blocks'
# COMPLETED_BLOCKS
AVERAGE_PROGRESS = 'average_progress'

SIMPLE_METRICS_NAMES = [
    UNIQUE_USERS, ENTERED_USERS, COMPLETED_PRODUCTS, USER_COMPLETED
]
