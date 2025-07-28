from django.db import models

class Transaction(models.Model):
    # ID é gerado automaticamente como chave primária
    id = models.BigAutoField(primary_key=True)

    # Campos obrigatórios
    wallet_id = models.CharField(max_length=255)  # equivalente ao string() do Laravel
    provider = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=255)

    # Campos opcionais (nullable)
    reference = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)

    # Campo com valor default
    status = models.CharField(max_length=255, default='pendente')

    # JSONField para armazenar dados brutos da resposta
    response_raw = models.JSONField(null=True, blank=True)

    # Campos automáticos de criação e atualização
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'  # garante o mesmo nome de tabela

    def __str__(self):
        return f"Transaction {self.id} - {self.status} - {self.amount}"
