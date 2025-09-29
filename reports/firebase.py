from firebase_admin import auth, firestore
from django.utils.timezone import now
from datetime import datetime, timedelta

# Inicializa o cliente Firestore
db = firestore.client()
FIRESTORE_PHONE_FIELD = "telefone"


def get_all_users():
    """
    Lê todos os documentos da coleção 'users' no Firebase Firestore.
    """
    users_ref = db.collection('users')
    docs = users_ref.stream()
    return [{ 'id': doc.id, **doc.to_dict() } for doc in docs]


def count_users():
    """
    Conta quantos documentos existem na coleção 'users' do Firebase.
    """
    users_ref = db.collection('users')
    return len(list(users_ref.stream()))

# def update_user(user_id, data):
#     """
#     Atualiza (ou adiciona) campos em um documento do usuário por ID.
#     """
#     user_ref = db.collection('users').document(user_id)
#     user_ref.set(data, merge=True)
#     print(f"[DEBUG] Dados atualizados no usuário: {user_id}")

def update_user(user_id, data):
    user_ref = db.collection('users').document(user_id)

    # Lê antes
    doc_before = user_ref.get()
    print(f"[DEBUG] Estado ANTES do update: {doc_before.to_dict()}")

    # Faz o update
    user_ref.set(data, merge=True)
    print(f"[DEBUG] Dados atualizados no usuário: {user_id}")

    # Lê depois
    doc_after = user_ref.get()
    updated_data = doc_after.to_dict()

    print(f"[DEBUG] Estado DEPOIS do update: {doc_after.to_dict()}")
    return updated_data



def update_user_by_phone(telefone, data):
    """
    Busca usuários por telefone e atualiza APENAS os campos enviados.
    Retorna a lista dos documentos atualizados.
    """
    users_ref = db.collection('users')
    print(f"[DEBUG] Consultando usuários com telefone == {telefone}")

    query = users_ref.where('telefone', '==', telefone)
    docs = list(query.stream())
    print(f"[DEBUG] Total de usuários encontrados: {len(docs)}")

    if not docs:
        print(f"[DEBUG] Nenhum usuário encontrado com telefone: {telefone}")
        raise ValueError(f"Nenhum usuário encontrado com telefone {telefone}")

    updated_users = []

    for doc in docs:
        current_data = doc.to_dict()
        print(f"[DEBUG] Usuario encontrado - ID: {doc.id}")
        print(f"[DEBUG] Dados atuais do usuário antes do update: {current_data}")

        # Faz update apenas dos campos enviados
        doc.reference.update(data)

        # Recupera os dados atualizados
        updated_doc = doc.reference.get()
        updated_data = updated_doc.to_dict()
        updated_data['id'] = updated_doc.id

        print(f"[DEBUG] Dados atualizados do usuário: {updated_data}")

        updated_users.append(updated_data)

    return updated_users


def get_users_by_telefone(telefone):
    """
    Busca usuários no Firestore filtrando por campo 'telefone'.
    """
    users_ref = db.collection('users')
    query = users_ref.where(FIRESTORE_PHONE_FIELD, '==', telefone)

    print(f"[DEBUG] Buscando usuário com telefone: {telefone}")

    docs = query.stream()
    return [{ 'id': doc.id, **doc.to_dict() } for doc in docs]


def create_user(data):
    telefone = data.get("telefone")
    if not telefone:
        raise ValueError("Campo 'telefone' é obrigatório.")

    # Verifica duplicado
    existing_users = db.collection("users").where(FIRESTORE_PHONE_FIELD, "==", telefone).stream()
    if any(existing_users):
        raise ValueError("Este número já está em uso.")

    # Se não enviou email, gera automático
    email = data.get("email") or f"{telefone}@gmail.com"

    # Cria usuário no Firebase Auth
    user_record = auth.create_user(
        email=email,
        password=data.get("password"),
        display_name=f"{data.get('name','')} {data.get('apelido','')}",
        phone_number=f"+258{telefone}"
    )
    uid = user_record.uid

    # Salva dados adicionais no Firestore
    new_user = {
        "id": uid,
        "name": data.get("name", ""),
        "apelido": data.get("apelido", ""),
        "gender": data.get("gender", ""),
        "birthYear": data.get("birthYear", ""),
        "provincia": data.get("provincia", ""),
        "telefone": telefone,
        "email": email,
        "password": data.get("password"),  # ⚠️ em produção, melhor não salvar em texto puro
        "image": data.get("image"),
        "createdAt": now().isoformat(),
        "updatedAt": now().isoformat(),
    }

    db.collection("users").document(uid).set(new_user)
    return new_user

# 🔥 FUNÇÕES DE RANKING CORRIGIDAS
def get_ranking_users():
    """
    Obtém todos os usuários do ranking da estrutura monthly_ranking
    """
    from datetime import datetime
    
    current_month = datetime.now().strftime('%Y-%m')
    
    try:
        # Acessa monthly_ranking/2025-09/users
        users_ref = db.collection('monthly_ranking').document(current_month).collection('users')
        docs = users_ref.stream()
        
        users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            
            # Busca informações completas do usuário
            try:
                user_main_data = get_user_details(user_data.get('uid'))
                user_data.update(user_main_data)
            except:
                # Se não encontrar usuário principal, usa apenas dados do ranking
                pass
            
            users.append(user_data)
        
        return users
    except Exception as e:
        print(f"Erro ao buscar usuários do ranking: {e}")
        return []

def get_current_ranking(limit=50):
    """
    Obtém o ranking atual ordenado por pontos - ESTRUTURA CORRIGIDA
    """
    from datetime import datetime
    
    current_month = datetime.now().strftime('%Y-%m')
    
    try:
        # Acessa monthly_ranking/2025-09/users e ordena por pontos
        users_ref = db.collection('monthly_ranking').document(current_month).collection('users')
        query = users_ref.order_by('points', direction=firestore.Query.DESCENDING)
        
        if limit:
            query = query.limit(limit)
        
        docs = query.stream()
        
        ranking = []
        posicao = 1
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            
            # Busca informações completas do usuário
            try:
                user_main_data = get_user_details(user_data.get('uid'))
                user_data.update(user_main_data)
            except:
                # Se não encontrar, usa dados básicos
                user_data.setdefault('name', '')
                user_data.setdefault('apelido', '')
                user_data.setdefault('telefone', '')
                user_data.setdefault('provincia', '')
                user_data.setdefault('gender', '')
                user_data.setdefault('birthYear', '')
            
            # Adiciona posição no ranking
            user_data['ranking_position'] = posicao
            user_data['ranking_points'] = user_data.get('points', 0)
            user_data['ranking_exams_count'] = user_data.get('exams', 0)
            
            posicao += 1
            ranking.append(user_data)
        
        return ranking
    except Exception as e:
        print(f"Erro ao buscar ranking atual: {e}")
        return []

def get_previous_month_winners():
    """
    Obtém os vencedores do mês anterior - ESTRUTURA CORRIGIDA
    """
    # Calcula mês anterior
    hoje = datetime.now()
    primeiro_dia_mes_atual = datetime(hoje.year, hoje.month, 1)
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
    mes_anterior = ultimo_dia_mes_anterior.strftime('%Y-%m')
    
    try:
        # Busca no monthly_ranking do mês anterior
        users_ref = db.collection('monthly_ranking').document(mes_anterior).collection('users')
        query = users_ref.order_by('points', direction=firestore.Query.DESCENDING).limit(10)
        
        docs = query.stream()
        winners = []
        posicao = 1
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            
            # Busca informações completas do usuário
            try:
                user_main_data = get_user_details(user_data.get('uid'))
                user_data.update(user_main_data)
            except:
                pass
            
            user_data['position'] = posicao
            user_data['ranking_points'] = user_data.get('points', 0)
            posicao += 1
            winners.append(user_data)
        
        return winners
    except Exception as e:
        print(f"Erro ao buscar vencedores do mês anterior: {e}")
        return []

def count_ranking_users():
    """
    Conta usuários que estão no ranking (baseado na estrutura monthly_ranking)
    """
    from datetime import datetime
    
    current_month = datetime.now().strftime('%Y-%m')
    
    try:
        users_ref = db.collection('monthly_ranking').document(current_month).collection('users')
        # Conta documentos onde points > 0
        query = users_ref.where('points', '>', 0)
        docs = list(query.stream())
        return len(docs)
    except Exception as e:
        print(f"Erro ao contar usuários do ranking: {e}")
        return 0

def update_user_ranking_points(user_id, points_to_add, exam_data=None):
    """
    Atualiza pontos de ranking de um usuário - ESTRUTURA CORRIGIDA
    """
    from datetime import datetime
    
    current_month = datetime.now().strftime('%Y-%m')
    
    try:
        # Referência para o usuário no monthly_ranking
        user_ref = db.collection('monthly_ranking').document(current_month).collection('users').document(user_id)
        
        # Verifica se já existe
        user_doc = user_ref.get()
        
        if user_doc.exists:
            # Atualiza usuário existente
            user_ref.update({
                'points': firestore.Increment(points_to_add),
                'exams': firestore.Increment(1),
                'updatedAt': now().isoformat()
            })
        else:
            # Cria novo usuário no ranking
            # Primeiro busca dados principais do usuário
            user_main_data = get_user_details(user_id)
            
            user_data = {
                'uid': user_id,
                'name': f"{user_main_data.get('name', '')} {user_main_data.get('apelido', '')}".strip(),
                'photo': user_main_data.get('image', ''),
                'points': points_to_add,
                'exams': 1,
                'month': current_month,
                'updatedAt': now().isoformat(),
                'createdAt': now().isoformat()
            }
            user_ref.set(user_data)
        
        # Registra no histórico do exame se fornecido
        if exam_data:
            exam_history_ref = db.collection('user_exam_history').document()
            exam_history_ref.set({
                'user_id': user_id,
                'exam_id': exam_data.get('examId'),
                'points_earned': points_to_add,
                'total_correct': exam_data.get('totalSuccess', 0),
                'total_questions': exam_data.get('totalQuestions', 0),
                'category': exam_data.get('categoryName'),
                'passed': exam_data.get('passed', False),
                'completed_at': now().isoformat(),
                'month': current_month
            })
        
        # Retorna os dados atualizados
        updated_doc = user_ref.get()
        return updated_doc.to_dict()
        
    except Exception as e:
        print(f"Erro ao atualizar pontos do ranking: {e}")
        raise e

def save_monthly_ranking_snapshot():
    """
    Salva um snapshot do ranking no final do mês - ESTRUTURA CORRIGIDA
    """
    from datetime import datetime
    
    current_month = datetime.now().strftime('%Y-%m')
    current_ranking = get_current_ranking(limit=100)
    
    # Salva snapshot
    ranking_snapshot_ref = db.collection('ranking_history').document()
    snapshot_data = {
        'month': current_month,
        'captured_at': now().isoformat(),
        'top_100': current_ranking
    }
    ranking_snapshot_ref.set(snapshot_data)
    
    # Salva top 10 como vencedores
    for i, user in enumerate(current_ranking[:10], 1):
        winner_ref = db.collection('ranking_winners').document()
        winner_ref.set({
            'user_id': user.get('uid', user.get('id')),
            'user_name': user.get('name', ''),
            'user_photo': user.get('photo', ''),
            'points': user.get('points', user.get('ranking_points', 0)),
            'position': i,
            'month': current_month,
            'awarded_at': now().isoformat()
        })
    
    return snapshot_data

def get_user_details(user_id):
    """
    Obtém detalhes completos de um usuário específico
    """
    user_ref = db.collection('users').document(user_id)
    doc = user_ref.get()
    
    if not doc.exists:
        raise ValueError(f"Usuário com ID {user_id} não encontrado")
    
    user_data = doc.to_dict()
    user_data['id'] = doc.id
    
    # Garante que todos os campos existam
    campos_obrigatorios = {
        'name': '',
        'apelido': '',
        'gender': '',
        'birthYear': '',
        'provincia': '',
        'telefone': '',
        'email': '',
        'isPro': False,
        'acceptedRanking': False,
        'createdAt': '',
        'updatedAt': ''
    }
    
    for campo, valor_padrao in campos_obrigatorios.items():
        user_data.setdefault(campo, valor_padrao)
    
    return user_data

def update_user_ranking(user_id, pontos=None, nivel=None, premiado=None):
    """
    Atualiza informações de ranking de um usuário
    """
    user_ref = db.collection('users').document(user_id)
    
    update_data = {
        'updatedAt': now().isoformat()
    }
    
    if pontos is not None:
        update_data['ranking_points'] = pontos
    
    if nivel is not None:
        update_data['ranking_level'] = nivel
    
    if premiado is not None:
        update_data['premiado'] = premiado
    
    user_ref.set(update_data, merge=True)
    
    # Retorna os dados atualizados
    updated_doc = user_ref.get()
    return updated_doc.to_dict()