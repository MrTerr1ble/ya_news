from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='TITLE',
        text='TEXT'
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='COMMENT TEXT'
    )


@pytest.fixture
def create_news():
    today = timezone.now()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(news_list)


@pytest.fixture
def create_comments(create_news, author):
    now = timezone.now()
    comments = [
        Comment(
            news=create_news,
            author=author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        )
        for index in range(10)
    ]
    Comment.objects.bulk_create(comments)
    return comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }
