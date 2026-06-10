"""
Cria um superuser a partir de variáveis de ambiente (idempotente).

Variáveis lidas:
- DJANGO_SUPERUSER_USERNAME
- DJANGO_SUPERUSER_EMAIL    (opcional, default vazio)
- DJANGO_SUPERUSER_PASSWORD

Se qualquer das obrigatórias estiver vazia, o comando sai sem fazer nada
(assim ele é seguro de rodar em todo deploy, mesmo depois que você apagar
a senha das Environment Properties).
"""

import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria superuser a partir das variáveis de ambiente (idempotente).'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()

        if not username or not password:
            self.stdout.write('DJANGO_SUPERUSER_USERNAME/PASSWORD vazios; pulando.')
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True},
        )

        # Sempre garante flags de superuser e atualiza a senha
        user.is_staff = True
        user.is_superuser = True
        if email:
            user.email = email
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" criado.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" atualizado (senha redefinida).'))
