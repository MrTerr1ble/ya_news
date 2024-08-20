import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

User = get_user_model()


@pytest.mark.django_db
class TestHomePage:

    HOME_URL = reverse("news:home")

    def test_news_count(self, client, create_news):
        response = client.get(self.HOME_URL)
        object_list = response.context["object_list"]
        news_count = object_list.count()
        assert news_count == NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client, create_news):
        response = client.get(self.HOME_URL)
        object_list = response.context["object_list"]
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates


@pytest.mark.django_db
class TestDetailPage:
    def test_comments_order(self, client, news):
        detail_url = reverse("news:detail", args=(news.id,))
        response = client.get(detail_url)
        news = response.context["news"]
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    @pytest.mark.parametrize(
        "parametrized_client, comment_form",
        (
            (pytest.lazy_fixture("author_client"), True),
            (pytest.lazy_fixture("not_author_client"), False),
        ),
    )
    def test_different_clients_has_form(
        self, parametrized_client, comment_form, comment
    ):
        detail_url = reverse("news:detail", args=(comment.id,))
        response = parametrized_client.get(detail_url)
        if comment_form:
            assert "form" in response.context
            assert isinstance(response.context["form"], CommentForm)
        else:
            assert (
                "form" not in response.context
                or not response.context["form"].is_bound
            )
