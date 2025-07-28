from django.urls import path
from .views import (
    unified_transactions,
    list_firebase_users,
    firebase_user_count,
    filter_users_by_phone,
    update_user_by_id,
    update_user_by_phone_view
)

urlpatterns = [
    path('transactions/', unified_transactions),
    path('clients/', list_firebase_users),
    path('clients/count/', firebase_user_count),
    path('clients/filter/', filter_users_by_phone),
    path('clients/<str:user_id>/', update_user_by_id),
    path('clients/byPhone/', update_user_by_phone_view),  

]
