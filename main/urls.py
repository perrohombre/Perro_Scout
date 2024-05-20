from django.urls import path
from .views import player_list, test_db_connection
from .api_views import PlayerList  # Importujemy PlayerList z api_views
from .api_chatbot_views import ChatbotAPIView

urlpatterns = [
    path('', player_list, name='home'),
    path('players/', player_list, name='player_list'),
    path('api/players/', PlayerList.as_view(), name='player_list'),
    path('test_db/', test_db_connection, name='test_db'),
     path('api/chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
]