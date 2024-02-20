
# Django Example 

Note: The local_settings.py file is typically added to the .gitignore file to ensure that sensitive information, such as passwords or API keys, is not committed to version control.


# Setting up local_settings.py

1. Clone the repository to your local machine:
2. Create a new file called local_settings.py in the root directory of your project.
3. Open the local_settings.py file in a text editor and add the following content:

```python
# local_settings.py

# Development mode
IS_DEVEL = True

# Allowed hosts
ALLOWED_HOSTS = ["*"]

# Email configuration
SET_EMAIL_HOST_USER_LOCAL = "qasemt@gmail.com"
SET_EMAIL_HOST_PASSWORD_LOCAL = "******"
```

# Test products

```
python manage.py test apps.products.tests.test_models
python manage.py test apps.products.tests.test_views
```
