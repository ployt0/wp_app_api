"""
Pythonised https://developer.wordpress.org/rest-api/reference/media/
A config file is required to contain information for accessing the WordPress
installation under test. This can remain outside of source control and will
take the form:

{
  "api": {
    "host_url": "https://localhost:6666",
    "user": "FRED_TEST",
    "password": "alls here bees prnt able F00B"
    "cert_name": "path/to/tls/cert"
  }
}
"""
import base64
import datetime
import json
import os.path
from typing import Optional, List, Dict

import requests


class WP_API:
    def __init__(self, config_file="config.json"):
        """Loading config from json outside of source control."""
        with open(config_file) as f:
            config = json.load(f)["api"]
            host_url = config["host_url"]
            credentials = config["user"] + ':' + config["password"]
            # Not optional, application passwords require it.
            self.name_of_cert = config["cert_name"]
            self.api_url = "{}/wp-json/wp/v2/".format(host_url)
            token = base64.b64encode(credentials.encode())
            self.header = {'Authorization': 'Basic ' + token.decode('utf-8')}

    def get_request_args(self, endpoint, headers, **kwargs) -> dict:
        return {
            "url": self.api_url + endpoint,
            "headers": headers if headers else self.header,
            "verify": self.name_of_cert,
            **kwargs
        }

    def get(self, endpoint, **kwargs) -> requests.Response:
        return requests.get(
            **self.get_request_args(
                endpoint, self.header, **kwargs))

    def delete(self, endpoint, **kwargs) -> requests.Response:
        return requests.delete(
            **self.get_request_args(
                endpoint, self.header, **kwargs))

    def post(self, endpoint, headers=None, **kwargs) -> requests.Response:
        return requests.post(
            **self.get_request_args(
                endpoint, headers if headers else self.header, **kwargs))

    def delete_all_my(self, noun):
        all_my_things = self.get_all_my_things(noun)
        deletable_ids = {x["id"] for x in all_my_things
                         if x["id"] != 1 or noun != "categories"}
        for thing_id in deletable_ids:
            del_result = self.delete(
                "{}/{}?force=true".format(noun, thing_id))
            assert del_result.ok
        number_after_deletion = len(self.get_all_my_things(noun))
        return len(all_my_things), number_after_deletion

    def get_all_my_things(self, noun) -> List[dict]:
        my_id = self.fetch_one("users/me", {})["id"]
        all_my_things = self.fetch_all(noun, {"author": my_id})
        if noun == "posts":
            all_my_things += self.fetch_all(
                noun, {"author": my_id, "status": "draft"})
        return all_my_things

    def create_category_or_tag(
            self,
            plural_noun: str,
            name: str,
            description: str,
            slug: Optional[str] = None,
            parent_category: Optional[int] = None) -> requests.Response:
        """
        Creating a category requires more privileges than Author.
        Deleting a tag requires more privileges than Author.

        :param plural_noun: "categories" or "tags"
        :param name: Aiming for self documenting variable names here.
        :param description: As if the brief name doesn't say enough.
        :param slug: typically a stringified version of name, can be omitted,
            the server will provide one.
        :param parent_category: NA to tags. Optional in any case.
        :return: response
        """
        json = {
            "name": name,
            "description": description,
            "slug": slug
        }
        if parent_category:
            json["parent"] = parent_category
        response = self.post(plural_noun, json=json)
        return response

    @staticmethod
    def default_slug(name: str) -> str:
        """Replaces spaces and strokes with hyphens."""
        return name.lower().replace("/", "-").replace(" ", "-")

    @staticmethod
    def get_wp_time(any_dt: datetime) -> str:
        return any_dt.strftime("%Y-%m-%dT%H:%M:%S")

    def append_results(self, noun: str, page: int, results: list,
                       extra_params: dict) -> dict:
        """

        :param noun: may be posts,settings,categories.
        :param page: start from 1.
        :param results: to append to.
        :param extra_params: alias for requests.get's json.
        :return: response's header links, if any.
        """
        response = self.get(
            noun,
            json={
                **extra_params,
                **{
                    "page": page,
                    "per_page": 10
                }})
        results.extend(response.json())
        return response.links

    def fetch_one(self, endpoint: str, extra_params: Optional[Dict] = None)\
            -> dict:
        """
        :param endpoint: to be added to the base host URL.
        :param extra_params: alias for requests.get's json.
        :return: the one object.
        """
        response = self.get(
            endpoint,
            json=extra_params,
        )
        return response.json()

    def fetch_all(self, noun: str, extra_params: dict) -> list:
        """
        Ensure your user has permissions to fetch things. "settings" are off
        limits to authors.

        :param noun: may be posts,settings,categories.
        :param extra_params: alias for requests.get's json.
        :return: list of results.
        """
        results = []
        page = 1
        links = self.append_results(noun, page, results, extra_params)
        while "next" in links:
            page += 1
            links = self.append_results(noun, page, results, extra_params)
        return results

    def upload_media(self, media_path: str, new_name: str = None):
        """
        If the new_name is already in use, hyphen number suffixes are used.
        All the scaling we see with the web UI is performed, exactly the same,
        binary identical pngs.

        :param media_path: src path to image, or even video, maybe others.
        :param new_name: destination name, if omitted the basename of the source
            (leaf node) is used. If provided the suffix must match.
        :return: json response as dict
        """
        if new_name is None:
            new_name = os.path.basename(media_path)
        image_bytes = open(media_path, 'rb').read()
        # "Content-Type" should be something, but WordPress will correct it.
        mime_type = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }.get(media_path.split(".")[-1], "image/jpeg")
        # "Accept" makes no discernible difference.
        headers = {
            **self.header,
            **{
                "Content-Type": mime_type,
                "Accept": "application/json",
                "Content-Disposition": "attachment; filename=" + new_name,
            }}

        response = self.post(
            "media",
            headers=headers,
            data=image_bytes,
        )
        return response
