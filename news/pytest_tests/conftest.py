from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


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
    news = News.objects.create(
        title='TITLE',
        text='TEXT'
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='COMMENT TEXT'
    )
    return comment


@pytest.fixture
def create_news():
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
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
