"""
More detailed WP responses. In case we're interested.
"""
import datetime

from wp_api.api_app import WP_API


def delete_all_my(noun: str, wp_api: WP_API) -> int:
    number_needing_deletion, number_after_deletion =\
        wp_api.delete_all_my(noun)
    assert number_needing_deletion >= number_after_deletion
    return number_after_deletion


def setup_module(module):
    """It breaks tests if we already have the same tags or categories."""
    wp_api = WP_API()
    # delete_test_tags(wp_api)
    assert 0 == delete_all_my("media", wp_api)
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


def test_upload_media():
    wp_api = WP_API()
    src_path = "white_200x300.png"
    mime_type = {
        "png": "image/png",
        "jpg": "image/jpeg",
    }[src_path.split(".")[-1]]
    desired_name = "white_200x300.png"
    response = wp_api.upload_media(src_path, desired_name)
    assert response.ok
    jresp = response.json()
    media_id = jresp["id"]
    site_url = jresp["guid"]["rendered"].split("/wp-content")[0]
    final_name = jresp["media_details"]["file"]
    now_dt = datetime.datetime.utcnow()
    expectjson1l_waccept = {'guid': {
        'rendered': '{site_url}/wp-content/uploads/{final_name}'.format(
            final_name=final_name, site_url=site_url),
        'raw': '{site_url}/wp-content/uploads/{final_name}'.format(
            final_name=final_name, site_url=site_url)},
        'slug': 'white_200x300',
        'status': 'inherit',
        'type': 'attachment',
        'link': '{site_url}/white_200x300/'.format(site_url=site_url),
        'title': {'raw': 'white_200x300', 'rendered': 'white_200x300'},
        'author': 1,
        'comment_status': 'open',
        'ping_status': 'closed',
        'template': '',
        'meta': [],
        'permalink_template': '{site_url}/?attachment_id={media_id}'.format(
            media_id=media_id, site_url=site_url),
        'generated_slug': 'white_200x300',
        'description': {
            'raw': '',
            'rendered': f'<p class="attachment"><a href=\'{site_url}/wp-content/uploads'
                        f'/{now_dt.year}/{now_dt.month:02}/{desired_name}\'><img width="200" height="300" src='
                        f'"{site_url}/wp-content/uploads/{now_dt.year}/{now_dt.month:02}'
                        f'/{desired_name}" class="attachment-medium size-medium" alt="" '
                        f'loading="lazy" /></a></p>\n'},
        'caption': {'raw': '', 'rendered': ''},
        'alt_text': '',
        'media_type': 'image',
        'mime_type': mime_type,
        'media_details': {
            'width': 200, 'height': 300,
            'file': '{final_name}'.format(final_name=final_name),
            'filesize': 1076,
            'sizes': {'thumbnail': {
                'file': 'white_200x300-150x150.png', 'width': 150, 'height': 150,
                'filesize': 93, 'mime_type': mime_type,
                'source_url': f'{site_url}/wp-content/uploads/{now_dt.year}/{now_dt.month:02}/white_200x300-150x150.png'
            }, 'full': {
                'file': desired_name, 'width': 200, 'height': 300, 'mime_type': mime_type,
                'source_url': f'{site_url}/wp-content/uploads/{final_name}'}
            }, 'image_meta': {
                'aperture': '0', 'credit': '', 'camera': '', 'caption': '',
                'created_timestamp': '0', 'copyright': '', 'focal_length': '0',
                'iso': '0', 'shutter_speed': '0', 'title': '',
                'orientation': '0', 'keywords': []
            }},
        'post': None,
        'source_url': f'{site_url}/wp-content/uploads/{final_name}',
        'missing_image_sizes': [],
        '_links': {
            'self': [{'href': f'{site_url}/wp-json/wp/v2/media/{media_id}'}],
            'collection': [{'href': f'{site_url}/wp-json/wp/v2/media'}],
            'about': [{'href': f'{site_url}/wp-json/wp/v2/types/attachment'}],
            'author': [{'embeddable': True, 'href': f'{site_url}/wp-json/wp/v2/users/1'}],
            'replies': [{'embeddable': True, 'href': f'{site_url}/wp-json/wp/v2/comments?post={media_id}'}],
            'wp:action-unfiltered-html': [{'href': f'{site_url}/wp-json/wp/v2/media/{media_id}'}],
            'wp:action-assign-author': [{'href': f'{site_url}/wp-json/wp/v2/media/{media_id}'}],
            'curies': [{'name': 'wp', 'href': 'https://api.w.org/{rel}', 'templated': True}]
        }
    }
    for k, v in expectjson1l_waccept.items():
        assert jresp[k] == v

