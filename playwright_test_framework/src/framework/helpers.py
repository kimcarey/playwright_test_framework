"""
Helper classes for API testing validations.
Provides reusable validation methods to reduce test code duplication.
"""

from typing import Dict, Any, List, Optional


class APIValidations:
    """
    Validation helpers for common API response patterns.
    """

    @staticmethod
    async def validate_single_post(response, post_id):
        """
        Validate that a response contains a properly structured post.

        Args:
            response: APIResponseWrapper object
            post_id: Expected post ID
        """
        post = await response.json()
        assert post['id'] == post_id
        assert 'title' in post
        assert 'body' in post
        assert 'userId' in post

    @staticmethod
    async def validate_post_list(response, min_count=1):
        """
        Validate that a response contains a list of properly structured posts.

        Args:
            response: APIResponseWrapper object
            min_count: Minimum number of posts expected
        """
        posts = await response.json()
        assert isinstance(posts, list)
        assert len(posts) >= min_count

        # Check first post has required fields
        if posts:
            first_post = posts[0]
            required_fields = ['id', 'title', 'body', 'userId']
            for field in required_fields:
                assert field in first_post

    @staticmethod
    async def validate_json_contains_fields(response, required_fields: List[str]):
        """
        Validate that JSON response contains all required fields.

        Args:
            response: APIResponseWrapper object
            required_fields: List of field names that must be present
        """
        data = await response.json()
        for field in required_fields:
            assert field in data, f"Required field '{field}' not found in response"

    @staticmethod
    async def validate_json_field_value(response, field_name: str, expected_value):
        """
        Validate that a specific field in JSON response has expected value.

        Args:
            response: APIResponseWrapper object
            field_name: Name of the field to check
            expected_value: Expected value of the field
        """
        data = await response.json()
        assert field_name in data, f"Field '{field_name}' not found in response"
        assert data[field_name] == expected_value, f"Field '{field_name}' has value '{data[field_name]}', expected '{expected_value}'"


class ResponseValidations:
    """
    Validation helpers for HTTP response properties.
    """

    @staticmethod
    def validate_status_code(response, expected_status: int):
        """
        Validate response has expected status code.

        Args:
            response: APIResponseWrapper object
            expected_status: Expected HTTP status code
        """
        assert response.status == expected_status, f"Expected status {expected_status}, got {response.status}"

    @staticmethod
    def validate_content_type(response, expected_content_type: str = "application/json"):
        """
        Validate response Content-Type header.

        Args:
            response: APIResponseWrapper object
            expected_content_type: Expected Content-Type value
        """
        content_type = response.headers.get('content-type', '').lower()
        assert expected_content_type.lower() in content_type, f"Expected content type '{expected_content_type}', got '{content_type}'"


class DataValidations:
    """
    Validation helpers for data structure and content validation.
    """

    @staticmethod
    async def validate_json_schema_type(response, field_name: str, expected_type: type):
        """
        Validate that a field in JSON response is of expected type.

        Args:
            response: APIResponseWrapper object
            field_name: Name of the field to check
            expected_type: Expected Python type (int, str, list, dict, etc.)
        """
        data = await response.json()
        assert field_name in data, f"Field '{field_name}' not found in response"
        assert isinstance(data[field_name],
                          expected_type), f"Field '{field_name}' is {type(data[field_name])}, expected {expected_type}"

    @staticmethod
    async def validate_list_not_empty(response, field_name: Optional[str] = None):
        """
        Validate that response (or a field in response) is a non-empty list.

        Args:
            response: APIResponseWrapper object
            field_name: Optional field name to check, if None checks entire response
        """
        data = await response.json()

        if field_name:
            assert field_name in data, f"Field '{field_name}' not found in response"
            target = data[field_name]
        else:
            target = data

        assert isinstance(target, list), f"Expected list, got {type(target)}"
        assert len(target) > 0, "List is empty"
