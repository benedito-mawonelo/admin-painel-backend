from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transaction
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .firebase import (
    get_all_users,
    count_users,
    get_users_by_telefone,
    update_user,
    update_user_by_phone,
    create_user,
    
    # 🔥 NOVAS FUNÇÕES DE RANKING
    get_ranking_users,
    get_current_ranking,
    get_previous_month_winners,
    count_ranking_users,
    get_user_details,
    update_user_ranking,
    update_user_ranking_points,
    save_monthly_ranking_snapshot
)



@api_view(['GET'])
def unified_transactions(request):
    """
    Endpoint que devolve transações (MySQL) + dados de usuários (Firebase).
    """
    users = get_all_users()
    user_dict = { u['id']: u for u in users }

    transactions = Transaction.objects.all()

    result = []
    for t in transactions:
        user_info = user_dict.get(str(t.wallet_id), {})
        result.append({
            'id': t.id,
            'wallet_id': t.wallet_id,
            'provider': t.provider,
            'amount': str(t.amount),
            'telefone': t.phone,
            'reference': t.reference,
            'category': t.category,
            'status': t.status,
            'response_raw': t.response_raw,
            'created_at': t.created_at,
            'updated_at': t.updated_at,
            'user': user_info
        })

    return Response(result)


@api_view(['GET'])
def list_firebase_users(request):
    """
    Endpoint que devolve todos os usuários do Firebase.
    """
    users = get_all_users()
    return Response(users)


@api_view(['GET'])
def firebase_user_count(request):
    """
    Endpoint que devolve o número total de usuários no Firebase.
    """
    total = count_users()
    return Response({ 'total_users': total })


@api_view(['GET'])
def filter_users_by_phone(request):
    """
    Endpoint para buscar usuários do Firebase filtrados por telefone.
    Exemplo de uso:
    /api/users/filter/?telefone=841234567
    """
    telefone = request.GET.get('telefone')
    if not telefone:
        return Response({'error': 'Parâmetro "telefone" é obrigatório.'}, status=400)

    users = get_users_by_telefone(telefone)
    return Response(users)


@api_view(['PATCH'])
def update_user_by_id(request, user_id):
    """
    PATCH /api/users/<user_id>/
    Body: JSON com campos a atualizar
    """
    data = request.data
    print(f"[DEBUG] Dados recebidos no request: {data}")

    if not data:
        return Response({'error': 'Nenhum dado enviado.'}, status=400)

    try:
        updated_user_data = update_user(user_id, data)
        return Response(updated_user_data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    


# @api_view(['PATCH'])
def update_user_by_phone_view(request):
    """
    Atualiza atributos de usuários no Firebase pelo campo 'telefone'.
    """
    telefone = request.data.get('telefone')
    print(f"[DEBUG] Telefone recebido para atualização: {telefone}")

    if not telefone:
        return Response({'error': 'Campo "telefone" é obrigatório.'}, status=400)

    # Remove 'telefone' dos dados a atualizar
    update_data = {k: v for k, v in request.data.items() if k != 'telefone'}
    print(f"[DEBUG] Dados para atualização: {update_data}")

    if not update_data:
        return Response({'error': 'Nenhum dado para atualizar.'}, status=400)

    try:
        updated_users = update_user_by_phone(telefone, update_data)
        return Response({
            'message': 'Usuário(s) atualizado(s) com sucesso.',
            'users': updated_users
        })

    except ValueError as ve:
        print(f"[DEBUG] Erro de valor: {str(ve)}")
        return Response({'error': str(ve)}, status=404)
    except Exception as e:
        print(f"[DEBUG] Erro inesperado: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def register_user(request):
    """
    POST /api/clients/register/
    Registra um novo usuário no Firebase.
    """
    try:
        user = create_user(request.data)
        return Response({"message": "Usuário registrado com sucesso!", "user": user}, status=201)
    except ValueError as ve:
        return Response({"error": str(ve)}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
    
    
# 🔥 NOVAS VIEWS DE RANKING

# @api_view(['GET'])
# def ranking_dashboard(request):
#     """
#     Endpoint que retorna todas as informações para o dashboard de ranking
#     """
#     try:
#         # Número total de usuários no ranking
#         total_ranking_users = count_ranking_users()
        
#         # Ranking atual
#         current_ranking = get_current_ranking(limit=50)
        
#         # Vencedores do mês anterior
#         previous_winners = get_previous_month_winners()
        
#         # Estatísticas adicionais
#         total_users = count_users()
        
#         return Response({
#             'total_ranking_users': total_ranking_users,
#             'total_users': total_users,
#             'current_ranking': current_ranking,
#             'previous_winners': previous_winners,
#             'ranking_percentage': round((total_ranking_users / total_users * 100), 2) if total_users > 0 else 0
#         })
        
#     except Exception as e:
#         return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def ranking_dashboard(request):
    """
    Endpoint SIMPLIFICADO para produção - apenas dados essenciais
    """
    try:
        # Apenas dados críticos para o dashboard
        total_ranking_users = count_ranking_users()
        total_users = count_users()
        
        # Ranking apenas top 10 para performance
        current_ranking = get_current_ranking(limit=10)
        
        # Vencedores anteriores (limitado)
        previous_winners = get_previous_month_winners()[:5]  # Apenas top 5
        
        return Response({
            'total_ranking_users': total_ranking_users,
            'total_users': total_users,
            'current_ranking': current_ranking,
            'previous_winners': previous_winners,
            'ranking_percentage': round((total_ranking_users / total_users * 100), 2) if total_users > 0 else 0,
            'status': 'success',
            'performance_optimized': True
        })
        
    except Exception as e:
        # Fallback básico se houver erro
        return Response({
            'total_ranking_users': 0,
            'total_users': 0,
            'current_ranking': [],
            'previous_winners': [],
            'ranking_percentage': 0,
            'status': 'fallback',
            'error': str(e)
        }, status=200)  # Sempre retorna 200 mesmo com erro
        
        
@api_view(['GET'])
def current_ranking(request):
    """
    Endpoint que retorna apenas o ranking atual
    """
    try:
        limit = request.GET.get('limit', 50)
        ranking = get_current_ranking(limit=int(limit))
        return Response(ranking)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def previous_winners(request):
    """
    Endpoint que retorna os vencedores do mês anterior
    """
    try:
        winners = get_previous_month_winners()
        return Response(winners)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def user_details(request, user_id):
    """
    Endpoint que retorna detalhes completos de um usuário
    """
    try:
        user_details = get_user_details(user_id)
        return Response(user_details)
    except ValueError as ve:
        return Response({'error': str(ve)}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['PATCH'])
def update_user_ranking_view(request, user_id):
    """
    Endpoint para atualizar informações de ranking de um usuário
    """
    try:
        pontos = request.data.get('pontos')
        nivel = request.data.get('nivel')
        premiado = request.data.get('premiado')
        
        updated_user = update_user_ranking(user_id, pontos, nivel, premiado)
        return Response(updated_user)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def add_ranking_points(request, user_id):
    """
    Endpoint para adicionar pontos de ranking a um usuário
    """
    try:
        points = request.data.get('points', 0)
        exam_data = request.data.get('exam_data', {})
        
        if points <= 0:
            return Response({'error': 'Pontos devem ser maiores que zero'}, status=400)
        
        updated_user = update_user_ranking_points(user_id, points, exam_data)
        
        if updated_user is None:
            return Response({
                'message': 'Usuário não elegível para ranking (não é PRO ou não aceitou)',
                'points_added': 0
            }, status=200)
        
        return Response({
            'message': 'Pontos adicionados com sucesso',
            'points_added': points,
            'current_points': updated_user.get('ranking_points', 0),
            'user': updated_user
        })
        
    except ValueError as ve:
        return Response({'error': str(ve)}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def ranking_stats(request):
    """
    Endpoint que retorna estatísticas do ranking - CORRIGIDA
    """
    try:
        total_ranking_users = count_ranking_users()
        total_users = count_users()
        
        # Obter distribuição por nível e província dos usuários do ranking
        ranking_users = get_current_ranking(limit=1000)  # Busca todos para estatísticas
        
        niveis = {}
        provincias = {}
        
        for user_data in ranking_users:
            # Distribuição por nível (baseado em pontos)
            pontos = user_data.get('points', user_data.get('ranking_points', 0))
            if pontos >= 100:
                nivel = "Expert"
            elif pontos >= 50:
                nivel = "Avançado"
            elif pontos >= 20:
                nivel = "Intermediário"
            else:
                nivel = "Iniciante"
            
            niveis[nivel] = niveis.get(nivel, 0) + 1
            
            # Distribuição por província
            provincia = user_data.get('provincia', 'Não informada')
            provincias[provincia] = provincias.get(provincia, 0) + 1
        
        return Response({
            'total_ranking_users': total_ranking_users,
            'total_users': total_users,
            'ranking_percentage': round((total_ranking_users / total_users * 100), 2) if total_users > 0 else 0,
            'distribution_by_level': niveis,
            'distribution_by_province': provincias,
            'current_month': datetime.now().strftime('%Y-%m')
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
@api_view(['POST'])
def create_ranking_snapshot(request):
    """
    Endpoint para criar um snapshot do ranking (usar no final do mês)
    """
    try:
        snapshot = save_monthly_ranking_snapshot()
        return Response({
            'message': 'Snapshot do ranking criado com sucesso',
            'snapshot': snapshot
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def ranking_users_list(request):
    """
    Endpoint que retorna todos os usuários do ranking (com filtros)
    """
    try:
        # Filtros opcionais
        provincia = request.GET.get('provincia')
        nivel = request.GET.get('nivel')
        min_points = request.GET.get('min_points', 0)
        
        users = get_ranking_users()
        
        # Aplicar filtros
        if provincia:
            users = [u for u in users if u.get('provincia') == provincia]
        
        if nivel:
            users = [u for u in users if u.get('ranking_level') == int(nivel)]
        
        if min_points:
            users = [u for u in users if u.get('ranking_points', 0) >= int(min_points)]
        
        return Response(users)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
    
from .models import Video
from .serializers import VideoSerializer

@api_view(['GET'])
@permission_classes([AllowAny]) 
def get_current_video(request):
    """
    Endpoint que retorna o vídeo atual da premiação
    """
    try:
        video = Video.objects.filter(active=True).first()
        if video:
            serializer = VideoSerializer(video)
            return Response(serializer.data)
        return Response({'message': 'Nenhum vídeo ativo encontrado'}, status=404)
    except Exception as e:
        logger.exception("Erro ao buscar vídeo atual")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def create_video(request):
    """
    Endpoint para adicionar um novo vídeo do YouTube
    """
    try:
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            # Se este vídeo for marcado como ativo, desativa os outros
            if serializer.validated_data.get('active', False):
                Video.objects.filter(active=True).update(active=False)
            
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    except Exception as e:
        logger.exception("Erro ao listar vídeos")
        return Response({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_video(request, video_id):
    """
    Endpoint para deletar um vídeo
    """
    try:
        video = Video.objects.get(id=video_id)
        video.delete()
        return Response({'message': 'Vídeo deletado com sucesso'}, status=200)
    except Video.DoesNotExist:
        return Response({'error': 'Vídeo não encontrado'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['PATCH'])
def set_active_video(request, video_id):
    """
    Endpoint para definir um vídeo como ativo
    """
    try:
        # Desativa todos os vídeos primeiro
        Video.objects.filter(active=True).update(active=False)
        
        # Ativa o vídeo específico
        video = Video.objects.get(id=video_id)
        video.active = True
        video.save()
        
        serializer = VideoSerializer(video)
        return Response(serializer.data)
    except Video.DoesNotExist:
        return Response({'error': 'Vídeo não encontrado'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def list_videos(request):
    """
    Endpoint que retorna todos os vídeos
    """
    try:
        videos = Video.objects.all().order_by('-created_at')
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)