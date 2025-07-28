from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transaction
from .firebase import (
    get_all_users,
    count_users,
    get_users_by_telefone,
    update_user,
    update_user_by_phone
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
