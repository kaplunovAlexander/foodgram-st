from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from .pagination import UserPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          SubscriptionSerializer)

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = UserPagination

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["put", "delete"],
        url_path="me/avatar",
    )
    def avatar(self, request):
        user = request.user

        if request.method == "PUT":
            serializer = AvatarSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update(user, serializer.validated_data)
                avatar_url = request.build_absolute_uri(user.avatar.url)
                return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            user.avatar.delete(save=True)
            return Response(
                {"detail": "Avatar deleted"}, status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
    )
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(followers__user=user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
    )
    def subscribe(self, request, id=None):
        user = request.user
        try:
            author = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(
                {"errors": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "POST":
            if user == author:
                return Response(
                    {"errors": "Нельзя подписаться на себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"errors": "Уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author,
                context={
                    "request": request,
                    "recipes_limit": request.query_params.get("recipes_limit"),
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            deleted, _ = Subscription.objects.filter(user=user, author=author).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
