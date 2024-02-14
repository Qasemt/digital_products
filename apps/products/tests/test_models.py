from django.test import TestCase
from ..models import Category


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Category.objects.create(title="Parent Category")
        Category.objects.create(title="Child Category", parent_id=1)

    def test_parent_category(self):
        parent_category = Category.objects.get(id=1)
        self.assertEqual(parent_category.title, "Parent Category")
        self.assertIsNone(parent_category.parent)
        self.assertTrue(parent_category.is_enable)

    def test_child_category(self):
        child_category = Category.objects.get(id=2)
        self.assertEqual(child_category.title, "Child Category")
        self.assertEqual(child_category.parent_id, 1)
        self.assertTrue(child_category.is_enable)
