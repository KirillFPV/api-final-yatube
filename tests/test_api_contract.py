"""Проверки изоляции данных и граничных случаев из документации API."""

from io import BytesIO

from django.db import IntegrityError, transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import pytest

from posts.models import Comment, Follow, Post


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('method', ('get', 'post'))
def test_comments_for_missing_post(user_client, method):
    response = getattr(user_client, method)(
        '/api/v1/posts/999999/comments/', {'text': 'Комментарий'},
    )
    assert response.status_code == 404
    assert not Comment.objects.exists()


@pytest.mark.parametrize('method', ('get', 'put', 'patch', 'delete'))
def test_comment_is_unavailable_under_another_post(
    user_client, post, comment_1_another_post, method,
):
    response = getattr(user_client, method)(
        f'/api/v1/posts/{post.pk}/comments/{comment_1_another_post.pk}/',
        {'text': 'Изменённый текст'},
    )
    assert response.status_code == 404
    comment_1_another_post.refresh_from_db()
    assert comment_1_another_post.text == 'Коммент 12'


def test_comment_cannot_change_author_or_post(
    user_client, user, another_user, post, another_post, comment_1_post,
):
    response = user_client.patch(
        f'/api/v1/posts/{post.pk}/comments/{comment_1_post.pk}/',
        {'text': 'Обновлено', 'author': another_user.pk,
         'post': another_post.pk},
        format='json',
    )
    assert response.status_code == 200
    comment_1_post.refresh_from_db()
    assert comment_1_post.author == user
    assert comment_1_post.post == post


def test_follow_list_contains_only_requesting_users_subscriptions(
    user_client, user, follow_1, follow_2, follow_3,
):
    response = user_client.get('/api/v1/follow/')
    assert response.status_code == 200
    assert response.json() == [
        {'user': user.username, 'following': follow_1.following.username},
    ]


def test_follow_cannot_spoof_subscriber(user_client, user, another_user, user_2):
    response = user_client.post(
        '/api/v1/follow/',
        {'user': user_2.username, 'following': another_user.username},
    )
    assert response.status_code == 201
    assert response.json()['user'] == user.username
    assert not Follow.objects.filter(user=user_2).exists()


def test_follow_duplicates_are_blocked_in_database(follow_1):
    with pytest.raises(IntegrityError), transaction.atomic():
        Follow.objects.create(
            user=follow_1.user, following=follow_1.following,
        )


@pytest.mark.parametrize('method', ('put', 'patch', 'delete'))
def test_follow_collection_disallows_other_methods(user_client, method):
    response = getattr(user_client, method)('/api/v1/follow/')
    assert response.status_code == 405


def test_post_author_is_set_from_token(user_client, user, another_user):
    response = user_client.post(
        '/api/v1/posts/',
        {'text': 'Публикация', 'author': another_user.username},
    )
    assert response.status_code == 201
    assert Post.objects.get(pk=response.json()['id']).author == user


def test_post_image_upload(user_client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    content = BytesIO()
    Image.new('RGB', (2, 2)).save(content, format='PNG')
    upload = SimpleUploadedFile(
        'test.png', content.getvalue(), content_type='image/png',
    )
    response = user_client.post(
        '/api/v1/posts/', {'text': 'Фото', 'image': upload},
        format='multipart',
    )
    assert response.status_code == 201
    post = Post.objects.get(pk=response.json()['id'])
    assert post.image.storage.exists(post.image.name)
    assert response.json()['image'].endswith(post.image.url)


def test_deleted_group_preserves_post(post, group_1):
    group_1.delete()
    post.refresh_from_db()
    assert post.group is None


def test_redoc_is_available(client):
    response = client.get('/redoc/')
    assert response.status_code == 200


def test_user_registration_is_not_exposed(client):
    response = client.post('/api/v1/users/', {'username': 'new-user'})
    assert response.status_code == 404
