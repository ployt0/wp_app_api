"""
Component testing against the default server imported in WP_API (as
config.json).
"""
import datetime
from typing import List
from unittest.mock import patch, Mock, sentinel, mock_open

from wp_api.api_app import WP_API


def test_get_self_user():
    wp_api = WP_API()
    myself = wp_api.fetch_one("users/me", {})
    assert "id" in myself


def test_get_users():
    wp_api = WP_API()
    result = wp_api.fetch_all("users", {})
    assert type(result) is list


def test_get_posts():
    wp_api = WP_API()
    result = wp_api.fetch_all("posts", {})
    assert type(result) is list


def test_get_categories():
    wp_api = WP_API()
    result = wp_api.fetch_all("categories", {})
    assert type(result) is list


def test_get_tags():
    wp_api = WP_API()
    result = wp_api.fetch_all("tags", {})
    assert type(result) is list


def test_get_media():
    wp_api = WP_API()
    result = wp_api.fetch_all("media", {})
    assert type(result) is list


def test_unit_upload_media():
    wp_api = WP_API()
    wp_api.post = Mock(WP_API.post, return_value=sentinel.response)
    mock_data = "data"
    with patch("builtins.open", mock_open(read_data=mock_data)) as mock_file:
        response = wp_api.upload_media("arbitrary.png", "creally.png")
        mock_file.assert_called_once_with("arbitrary.png", "rb")
    assert response == sentinel.response
    wp_api.post.assert_called_once()
    assert wp_api.post.mock_calls[0].kwargs["data"] == mock_data


def test_upload_media():
    wp_api = WP_API()
    response = wp_api.upload_media("white_200x300.png", "white_200x300.png")
    assert response.ok
    response = wp_api.upload_media("white_200x1024.png", "white_200x1024.png")
    assert response.ok


def test_upload_media_default_naming():
    wp_api = WP_API()
    media_path = "./white_200x300.png"
    new_name = "white_200x300.png"
    wp_api.post = Mock(WP_API.post, return_value=sentinel.response)
    mock_data = "data"
    with patch("builtins.open", mock_open(read_data=mock_data)) as mock_file:
        response = wp_api.upload_media(media_path)
    assert response == sentinel.response
    wp_api.post.assert_called_once()
    assert wp_api.post.mock_calls[0].kwargs["data"] == mock_data
    assert wp_api.post.mock_calls[0].kwargs["headers"]['Content-Disposition'] == 'attachment; filename={}'.format(new_name)


def test_categorised_create_post():
    wp_api = WP_API()
    category = get_cat_id_for_testing(wp_api)
    response = wp_api.post(
        "posts",
        json={
            "title": "My first post via API",
            "status": "publish",
            "content": """<p>This is going to look awful.</p>
<p>I think anything goes and for markdown
we have HTML</p>""",
            "categories": category,
            "date_gmt": WP_API.get_wp_time(datetime.datetime.utcnow())
        })
    assert response.ok


def get_cat_id_for_testing(wp_api):
    """Will return uncategorised, if CI/CD or "test cat" are unavailable."""
    category = 1
    for x in ["Test cat", "CI/CD", "CI-CD", "CICD"]:
        suitable_cat = wp_api.fetch_all("categories?search={}".format(x), {})
        if suitable_cat:
            category = suitable_cat[0]["id"]
            break
    return category


def test_update_post():
    wp_api = WP_API()
    post_list = wp_api.get_all_my_things("posts")
    response = wp_api.post(
        "posts/{}".format(post_list[0]["id"]),
        json={
            "title": "My ammended first post via API",
            "content": """<p>This is going to look awful.</p>
<p>I tried to prettify it with HTML</p>""",
        })
    assert response.ok


def test_delete_my_media():
    wp_api = WP_API()
    response = wp_api.upload_media("white_200x300.png", "white_200x300.png")
    assert response.ok
    assert 0 == delete_all_my("media", wp_api)


def delete_all_my(noun: str, wp_api: WP_API) -> int:
    number_needing_deletion, number_after_deletion =\
        wp_api.delete_all_my(noun)
    assert number_needing_deletion >= number_after_deletion
    return number_after_deletion


def test_get_wp_time():
    t = datetime.datetime(2022, 12, 2, 18, 00)
    t_str = WP_API.get_wp_time(t)
    assert t_str == '2022-12-02T18:00:00'
    t = datetime.datetime(2022, 6, 2, 18, 00)
    t_str = WP_API.get_wp_time(t)
    assert t_str == '2022-06-02T18:00:00'


def test_create_category():
    wp_api = WP_API()
    given_slug = "lemmesee"
    response = wp_api.create_category_or_tag(
        "categories", "test_name", "test_description can be wordier.",
        given_slug, None
    )
    assert response.ok
    assert response.json()["slug"] == given_slug


def test_create_category_gen_slug():
    wp_api = WP_API()
    cat_name = "cat Manoba"
    response = wp_api.create_category_or_tag(
        "categories", cat_name, "test_description can be wordier."
    )
    assert response.ok
    assert response.json()["slug"] == cat_name.lower().replace(" ", "-")


def test_create_tag():
    wp_api = WP_API()
    response = wp_api.create_category_or_tag(
        "tags", "test_name", "test_description can be wordier.",
        "i_wonder", None
    )
    assert response.ok


def test_fetch_all():
    wp_api = WP_API()
    assert 0 == delete_all_my("tags", wp_api)
    for tag_no in range(15):
        response = wp_api.create_category_or_tag(
            "tags", "tag_name_{}".format(tag_no),
            "test_description can be wordier."
        )
    result = wp_api.fetch_all("tags", {})
    assert len(result) == 15


def setup_module(module):
    """It breaks tests if we already have the same tags or categories."""
    wp_api = WP_API()
    # delete_test_tags(wp_api)
    assert 0 == delete_all_my("tags", wp_api)
    assert 1 == delete_all_my("categories", wp_api)


def teardown_module(module):
    """teardown any state after all tests herein have run."""
    wp_api = WP_API()
    assert 0 == delete_all_my("media", wp_api)
    assert 0 == delete_all_my("tags", wp_api)
    # The sample post gets deleted first time.
    assert 0 == delete_all_my("posts", wp_api)
    # Uncategorized can never be deleted.
    assert 1 == delete_all_my("categories", wp_api)


def search_tags(wp_api, query_str: str) -> List[dict]:
    """
    I recall only editors can delete tags, whilst Authors can create them.
    I wasn't sure if Authors really owned these, so I made them use
    IDENTIFYING_PREFIX and retrieved them in this function.

    Now I've got a dedicated test WP, and dedicated test Administrator.
    It's just a common search function now.
    """
    # This *only* searches tag names and slugs, case insensitive:
    filtered_tag_list = wp_api.fetch_all(
        "tags?search=" + query_str, {})
    return filtered_tag_list

