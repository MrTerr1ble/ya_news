from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from news.forms import CommentForm

User = get_user_model()


@pytest.mark.django_db
class TestHomePage:

    HOME_URL = reverse("news:home")

    def test_news_count(
        self, client, create_news
    ):
        response = client.get(self.HOME_URL)
        object_list = response.context["object_list"]
        news_count = object_list.count()
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(
        self, client, create_news
    ):
        response = client.get(self.HOME_URL)
        object_list = response.context["object_list"]
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates


@pytest.mark.django_db
class TestDetailPage:
    def test_comments_order(
        self, client, news
    ):
        detail_url = reverse("news:detail", args=(news.id,))
        response = client.get(detail_url)
        news = response.context["news"]
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(
        self, client, news
    ):
        detail_url = reverse("news:detail", args=(news.id,))
        response = client.get(detail_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(
        self, client, news, author
    ):
        detail_url = reverse("news:detail", args=(news.id,))
        client.force_login(author)
        response = client.get(detail_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
