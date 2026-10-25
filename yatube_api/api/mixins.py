from rest_framework import mixins, viewsets


class ListCreateViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для получения списка объектов и создания нового объекта."""
