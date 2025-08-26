"""
Example API tests showing how to use the framework with helper validations.
Uses JSONPlaceholder (a free fake API).
"""

import pytest
import pytest_asyncio
from framework.api_client import APIClient
from framework.helpers import APIValidations, ResponseValidations


class TestJSONPlaceholderAPI:
    """Example test class demonstrating the API testing framework."""

    @pytest_asyncio.fixture
    async def api_client(self):
        """Fixture that provides an API client for tests."""
        async with APIClient(base_url="https://jsonplaceholder.typicode.com") as client:
            yield client

    @pytest.mark.asyncio
    async def test_get_all_posts(self, api_client):
        """Test getting all posts - demonstrates basic GET request."""
        response = await api_client.get("/posts")

        # Using our custom assertion methods
        assert response.is_successful()
        ResponseValidations.validate_status_code(response, 200)

        await APIValidations.validate_post_list(response, min_count=0)

    @pytest.mark.asyncio
    async def test_get_single_post(self, api_client):
        """Test getting a specific post - demonstrates parameterized requests."""
        post_id = 1
        response = await api_client.get(f"/posts/{post_id}")

        assert response.is_successful()

        await APIValidations.validate_single_post(response, post_id)

    @pytest.mark.asyncio
    async def test_create_post(self, api_client):
        """Test creating a new post - demonstrates POST with JSON data."""
        new_post = {
            'title': 'Test Framework Post',
            'body': 'This post was created by our test framework!',
            'userId': 1
        }

        response = await api_client.post("/posts", data=new_post)

        assert response.is_successful()
        ResponseValidations.validate_status_code(response, 201)

        await APIValidations.validate_json_contains_fields(response, ['title', 'body', 'userId'])

    @pytest.mark.asyncio
    async def test_update_post(self, api_client):
        """Test updating a post - demonstrates PUT request."""
        post_id = 1
        updated_data = {
            'id': post_id,
            'title': 'Updated Title',
            'body': 'Updated body content',
            'userId': 1
        }

        response = await api_client.put(f"/posts/{post_id}", data=updated_data)

        assert response.is_successful()
        ResponseValidations.validate_status_code(response, 200)

        updated_post = await response.json()
        assert updated_post['title'] == updated_data['title']
        assert updated_post['body'] == updated_data['body']

    @pytest.mark.asyncio
    async def test_delete_post(self, api_client):
        """Test deleting a post - demonstrates DELETE request."""
        post_id = 1
        response = await api_client.delete(f"/posts/{post_id}")

        assert response.is_successful()
        ResponseValidations.validate_status_code(response, 200)

    @pytest.mark.asyncio
    async def test_404_error_handling(self, api_client):
        """Test how we handle client errors - demonstrates error checking."""
        response = await api_client.get("/posts/99999")  # Non-existent post

        assert response.is_client_error()
        ResponseValidations.validate_status_code(response, 404)
        assert not response.is_successful()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("post_id", [1, 2, 3, 4, 5])
    async def test_multiple_posts_exist(self, api_client, post_id):
        """Test that demonstrates parametrized testing - runs for multiple post IDs."""
        response = await api_client.get(f"/posts/{post_id}")

        assert response.is_successful()

        await APIValidations.validate_single_post(response, post_id)
