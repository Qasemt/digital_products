from unittest import TestCase
from apps.products.models import Category
from apps.products.serializers import CategorySerializer
from rest_framework.test import APIClient


class CategoryListViewTest(TestCase):
    def setUp(self):
        # Set up any necessary data for the test
        Category.objects.create(title="Test Category")

    def test_category_list_view(self):
        # Create an instance of the APIClient
        client = APIClient()

        # Send a GET request to the category list view
        response = client.get("/categories/")

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Retrieve the categories from the database
        categories = Category.objects.all()

        # Serialize the categories
        serializer = CategorySerializer(categories, many=True)

        # Assert that the response data matches the serialized data
        self.assertEqual(response.data, serializer.data)
