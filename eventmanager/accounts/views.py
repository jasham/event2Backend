from django.shortcuts import render
from .models import UserModel
from .serializers import AccountsSerializerPaid, AccountsSerializerGuest,MyTokenObtainPairSerializer,RefreshTokenSerializer,ChangePasswordSerializer
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
import string
import secrets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from rest_framework import permissions
from rest_framework.generics import GenericAPIView,UpdateAPIView
from rest_framework.views import APIView

# Create your views here.

class ChangePasswordView(UpdateAPIView):
        """
        An endpoint for changing password.
        """
        serializer_class = ChangePasswordSerializer
        model = UserModel
        permission_classes = (IsAuthenticated,)

        def get_object(self, queryset=None):
            obj = self.request.user
            return obj

        def update(self, request, *args, **kwargs):
            self.object = self.get_object()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Check old password
                if not self.object.check_password(serializer.data.get("old_password")):
                    return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
                # set_password also hashes the password that the user will get
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully',
                    'data': []
                }

                return Response(response)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
'''class TokenVerifyView(TokenViewBase):
    """
    Takes a token and indicates if it is valid.  This view provides no
    information about a token's fitness for a particular use.
    """
    serializer_class = serializers.TokenVerifySerializer'''
class Logout(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args):
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response({"Response":"successfully logged out."},status=status.HTTP_204_NO_CONTENT)

class UserViewSetPaid(viewsets.ModelViewSet):
    serializer_class = AccountsSerializerPaid
    queryset = UserModel.objects.all()
    permission_classes  = [permissions.AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser]
    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user_data={}
        user_data.update({"email":request.data['email']})
        user_data.update({"password":request.data['password']})
        user_data.update({"username":request.data['username']})
        sending_mail('email_template.txt','email_template.html',user_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserViewSetGuest(viewsets.ModelViewSet):
    serializer_class = AccountsSerializerGuest
    queryset = UserModel.objects.all()
    permission_classes  = [permissions.AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser]
    def create(self,request):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user_data={}
        user_data.update({"email":request.data['email']})
        user_data.update({"password":request.data['password']})
        user_data.update({"username":request.data['username']})
        sending_mail('email_template.txt','email_template.html',user_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
class ForgetPasswordView(APIView):
    def get(self,request):
        if(UserModel.objects.filter(email=request.query_params.get("email"))):
            requested_username=request.query_params.get("email")
            alphabet = string.ascii_letters + string.digits
            while True:
                changed_password = ''.join(secrets.choice(alphabet) for i in range(10))
                if (any(c.islower() for c in changed_password)
                        and any(c.isupper() for c in changed_password)
                        and sum(c.isdigit() for c in changed_password) >= 3):
                    break
            print(changed_password)
            new_password = make_password(changed_password)
            user= UserModel.objects.get(email=requested_username).username
            UserModel.objects.filter(email=requested_uesrname).update(password=new_password)
            user_data={}
            user_data.update({"email":requested_username})
            user_data.update({"password":changed_password})
            user_data.update({'username':user})
            sending_mail('resetpwd_template.txt','resetpwd_template.html',user_data)
            return Response({"Response":"successfully pasword changed. Please check your email."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"response":"Username doesn't exist"})

def sending_mail(arg1,arg2,user):
    msg_plain = render_to_string(arg1, {'username': user["username"],'password':user["password"]})
    msg_html = render_to_string(arg2, {'username': user["username"],'password':user["password"]})
    send_mail(
        'Medchip',
            msg_plain,
        'datasimulation.bot@gmail.com',
        [user["email"]],
        html_message=msg_html,
        fail_silently = True)


    # def post(self, request):
    #     print("Hello This ",request.data)

# class UserList(viewsets.ModelViewSet):
#     serializer_class = UserPerfect
#     queryset = UserNew.objects.all()
#     permission_classes  = [permissions.AllowAny]
#     authentication_classes = []
    # parser_classes = [MultiPartParser]
