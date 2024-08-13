from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import User
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, ChangePasswordSerializer


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
):
    """
    Updates , retrieves and Delete user accounts
    """

    queryset = User.objects.all()
    print(queryset)
    serializer_class = UserSerializer
    print("########################################################### serializer_class ",serializer_class)
    permission_classes = (IsUserOrReadOnly,)
    print("########################################################### permission_classes,",permission_classes)
    def partial_update(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        print(serializer,"####################################################",request.data)
        if serializer.is_valid():
            # Check old password
            user = User.objects.get(id=request.user.id)
            print("########################################################### user token,", user)

            # check old password 
            if not user.check_password(serializer.data.get("old_password")):

                return Response({"old_password": ["Wrong password."]}, status=400)

            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.save()
            
            response = {
                "status": "success",
                "code": 200,
                "message": "Password updated successfully",
                "data": [],
                }
            return Response(response)
        return Response(serializer.errors, status=400)


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    print(queryset, "#######################################################################")
    serializer_class = CreateUserSerializer
    # Allows access only to authenticated users.
    permission_classes = (AllowAny,)


class UserAuthToken(ObtainAuthToken):
    """Get or create a token for a user"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        print(request.data,"##################################")
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        print(token,"################################")
        
        return Response(
            {
                "token": token.key,
                "id": user.pk,
                'email': user.email,
                "is_superuser": user.is_superuser,

            }
        )

        