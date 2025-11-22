from django.contrib.auth import get_user_model
print(get_user_model().objects.filter(username='admin').exists())
