# users/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser, Role, UserActivity
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer, RoleSerializer, UserActivitySerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['phone', 'name', 'email']
    ordering_fields = ['name', 'email', 'phone', 'status', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        roles = self.request.query_params.getlist('roles')
        if roles:
            queryset = queryset.filter(roles__name__in=roles)
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        user.status = 'inactive' if user.status == 'active' else 'active'
        user.save()
        
        # Registrar atividade
        UserActivity.objects.create(
            user=user,
            title=f"Status {'ativado' if user.status == 'active' else 'desativado'}",
            description=f"O status do usuário foi alterado para {user.status}.",
            icon='toggle_' + user.status
        )
        
        return Response({'status': user.status}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = serializer.save()
        UserActivity.objects.create(
            user=user,
            title="Usuário criado",
            description=f"Usuário {user.name} foi criado.",
            icon="person_add"
        )

    def perform_update(self, serializer):
        user = serializer.save()
        UserActivity.objects.create(
            user=user,
            title="Perfil atualizado",
            description=f"Os dados do usuário {user.name} foram atualizados.",
            icon="edit"
        )

class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return UserActivity.objects.filter(user_id=user_id).order_by('-date')