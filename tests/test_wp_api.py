"""
Component testing against the default server imported in WP_API (as
config.json).
"""
import datetime

import sys
print(sys.path)

from wp_api.api_app import WP_API


# For use in naming stuff where we can't trace ownership to the user
# who is running these tests.
IDENTIFYING_PREFIX = "test220722_"


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


def test_upload_media():
    wp_api = WP_API()
    response = wp_api.upload_media("white_200x300.png", "white_200x300.png")
    assert response.ok
    response = wp_api.upload_media("white_200x1024.png", "white_200x1024.png")
    assert response.ok


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
    delete_all_my("media", wp_api)


def delete_all_my(noun, wp_api):
    number_needing_deletion, number_after_deletion =\
        wp_api.delete_all_my(noun)
    assert number_needing_deletion >= number_after_deletion
    assert number_after_deletion == 0


def test_get_wp_time():
    t = datetime.datetime(2022, 12, 2, 18, 00)
    t_str = WP_API.get_wp_time(t)
    assert t_str == '2022-12-02T18:00:00'
    t = datetime.datetime(2022, 6, 2, 18, 00)
    t_str = WP_API.get_wp_time(t)
    assert t_str == '2022-06-02T18:00:00FFF'


def teardown_module(module):
    """teardown any state after all tests herein have run."""
    wp_api = WP_API()
    delete_all_my("media", wp_api)
    delete_test_tags(wp_api)
    delete_all_my("posts", wp_api)


def delete_test_tags(wp_api):
    """
    Requires greated privileges than Author.
    Needs to be called before attempting to re-create a tag as auto
    renaming does not happen for duplicate tag names.
    """
    # This *only* searches tag names and slugs, case insensitive:
    filtered_tag_list = wp_api.fetch_all(
        "tags?search=" + IDENTIFYING_PREFIX, {})
    for tag in filtered_tag_list:
        if tag["name"].startswith(IDENTIFYING_PREFIX):
            del_result = wp_api.delete("{}/{}".format("tags", tag["id"]))
            assert del_result.ok

