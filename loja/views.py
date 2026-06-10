from django.shortcuts import render


def index(request):
    """Site da loja (interface web servida na raiz)."""
    return render(request, 'loja/index.html')
