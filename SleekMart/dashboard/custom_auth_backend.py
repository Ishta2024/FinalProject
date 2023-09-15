# from django.contrib.auth.backends import ModelBackend
# from .models import CustomUser

# class CustomAuthBackend(ModelBackend):
#     def authenticate(self, request, email=None, password=None,role=None, **kwargs):
#         try:
#             user = CustomUser.objects.get(email=email, role=role)
#         except CustomUser.DoesNotExist:
#             return None

#         if user.check_password(password) and self.user_can_authenticate(user):
#             return user

#     def get_user(self, user_id):
#         try:
#             return CustomUser.objects.get(pk=user_id)
#         except CustomUser.DoesNotExist:
#             return None
