from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_django.asserts import assertRedirects

User = get_user_model()


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous_user(
    db, client, name, news_object
):
    args = (news_object.id,) if news_object else ()
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:delete', pytest.lazy_fixture('comment')),
        ('news:edit', pytest.lazy_fixture('comment')),
    ),
)
def test_pages_availability_for_author_users(
    client, name, news_object, status
):
    url = reverse(name, args=(news_object.id,))
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:delete', pytest.lazy_fixture('comment')),
        ('news:edit', pytest.lazy_fixture('comment')),
    ),
)
def test_redirect_for_anonymous_client(
    db, client, name, news_object
):
    login_url = reverse('users:login')
    url = reverse(name, args=(news_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
