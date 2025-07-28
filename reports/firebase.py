from firebase_admin import firestore

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
