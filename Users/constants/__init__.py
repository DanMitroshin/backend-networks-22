from Users.constants.DEVICES import *
from Users.constants.REGISTRATION_PLATFORMS import *
from Users.constants.ACCESS_GROUPS import *
from .USER_SEX import *


ACCESS_TRIAL = "access_trial"
ACCESS_PURCHASED = "access_purchased"
ACCESS_GIFTED = "access_gifted"
ACCESS_PERMANENT = "access_permanent"

CONTENT_ACCESS_ROLES = (
    # Access group roles
    (ACCESS_TRIAL, 'On trial'),
    (ACCESS_PURCHASED, 'Purchased'),
    (ACCESS_GIFTED, 'Received as a gift'),
    (ACCESS_PERMANENT, 'Permanent access'),
)

CLASSROOM_ROLES = (
    ('classroom_owner', 'Classroom owner'),
    ('classroom_assistent', 'Assistent'),
    ('classroom_student', 'Student'),
)

ACCESS_GROUP_ROLES = CONTENT_ACCESS_ROLES + CLASSROOM_ROLES

BANNED_TYPES = [
    ('rat', 'Нельзя набирать очки в текущем рейтинге.'),
    ('name', 'Нельзя менять данные идентификации.'),
]

CAN_NOT_PARTICIPATE_IN_RATING_AND_EDIT_INFORMATION = 1
