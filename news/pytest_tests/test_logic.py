from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, news
):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, author, form_data, news
):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    new_comment = Comment.objects.get()
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    admin_client, news
):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, news, comment
):
    url = reverse('news:detail', args=(news.id,))
    url_to_comments = f'{url}#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assertRedirects(response, url_to_comments)
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client, comment, form_data, news
):
    url = reverse('news:detail', args=(news.id,))
    url_to_comments = f'{url}#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    comment.refresh_from_db()
    assertRedirects(response, url_to_comments)
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    admin_client, form_data, comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == comment_from_db.text


def test_user_cant_delete_comment_of_another_user(
    admin_client, comment
):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
