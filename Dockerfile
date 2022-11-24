FROM python:3.8.7-alpine as base
WORKDIR /app
RUN apk add --no-cache build-base
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
COPY requirements.txt .
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1
RUN apk add --no-cache libffi-dev openssl-dev python3-dev
RUN pip install -r requirements.txt

FROM base as release
EXPOSE 7002
WORKDIR /app/code
# CMD python manage.py runserver --settings APIBackendService.settings.development 0.0.0.0:7000
CMD [ \
"gunicorn", \
"--workers=3", \
"--bind", \
"0.0.0.0:7002", \
"APIBackendService.wsgi:application" \
]
