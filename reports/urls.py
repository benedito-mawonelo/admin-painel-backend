from django.urls import path
from .views import (
    unified_transactions,
    list_firebase_users,
    firebase_user_count,
    filter_users_by_phone,
    update_user_by_id,
    update_user_by_phone_view,
    register_user
)
from . import views

urlpatterns = [
    path('transactions/', unified_transactions),
    path('clients/', list_firebase_users),
    path('clients/count/', firebase_user_count),
    path('clients/filter/', filter_users_by_phone),
    path('clients/<str:user_id>/', update_user_by_id),
    path('clients/byPhone/', update_user_by_phone_view),
    path('client/register/', register_user),   


 # 🔥 NOVAS URLs DE RANKING
    path('ranking/dashboard/', views.ranking_dashboard, name='ranking-dashboard'),
    path('ranking/current/', views.current_ranking, name='current-ranking'),
    path('ranking/previous-winners/', views.previous_winners, name='previous-winners'),
    path('ranking/stats/', views.ranking_stats, name='ranking-stats'),
    path('ranking/snapshot/', views.create_ranking_snapshot, name='create-ranking-snapshot'),
    path('ranking/users/', views.ranking_users_list, name='ranking-users-list'),
    
    # 🔥 URLs DE USUÁRIOS ESPECÍFICOS
    path('users/<str:user_id>/details/', views.user_details, name='user-details'),
    path('users/<str:user_id>/update-ranking/', views.update_user_ranking_view, name='update-user-ranking'),
    path('users/<str:user_id>/add-ranking-points/', views.add_ranking_points, name='add-ranking-points'),
    
    
    # URLs para gerenciar vídeos
    path('videos/', views.list_videos, name='list_videos'),
    path('videos/current/', views.get_current_video, name='get_current_video'),
    path('videos/create/', views.create_video, name='create_video'),
    path('videos/<int:video_id>/delete/', views.delete_video, name='delete_video'),
    path('videos/<int:video_id>/set-active/', views.set_active_video, name='set_active_video'),
]
