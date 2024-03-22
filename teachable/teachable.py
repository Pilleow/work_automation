import requests
import urllib.request
import json

from teachable.teachable_authorizer import TeachableAuthorizer


class Teachable(TeachableAuthorizer):
    def get_course(self, course_id) -> dict:
        """
        https://docs.teachable.com/reference/showcourse
        :param course_id:
        :return:
        """
        url = f"https://developers.teachable.com/v1/courses/{course_id}"
        response = self._send_request(url)
        return response.json()

    def get_lecture(self, course_id, lecture_id) -> dict:
        """
        https://docs.teachable.com/reference/showlecture
        :param course_id:
        :param lecture_id:
        :return:
        """
        url = f"https://developers.teachable.com/v1/courses/{course_id}/lectures/{lecture_id}"
        response = self._send_request(url)
        return response.json()

    def get_video_data(self, course_id, lecture_id, video_id) -> dict:
        """
        https://docs.teachable.com/reference/showlecture
        :param course_id:
        :param lecture_id:
        :param video_id:
        :return:
        """
        url = f"https://developers.teachable.com/v1/courses/{course_id}/lectures/{lecture_id}/videos/{video_id}"
        response = self._send_request(url)
        return response.json()

    def get_static_url(self, url, filename):
        urllib.request.urlretrieve(url, filename)

    def authorize(self, teachable_key_path):
        with open(teachable_key_path, "r") as f:
            self.key = json.load(f)["key"]

    def _send_request(self, url, use_json: bool = True):
        response = requests.get(url, headers=self._build_headers())
        if response.status_code != 200:
            if use_json:
                raise Exception(f"GET Request returned code {response.status_code}. Details:\n{response.json()}")
            else:
                raise Exception(f"GET Request returned code {response.status_code}. Details:\n{response.content}")
        return response

    def _build_headers(self):
        return {
            "accept": "application/json",
            "apiKey": self.key
        }
