from .models import Notificacao


def grupos_usuario(request):
    if not request.user.is_authenticated:
        return {
            'ui_rh': False,
            'ui_admin': False,
            'notificacoes': [],
            'total_nao_lidas': 0,
        }

    notificacoes = Notificacao.objects.filter(
        usuario=request.user
    ).order_by('-data_criacao')[:5]

    total_nao_lidas = Notificacao.objects.filter(
        usuario=request.user,
        lida=False
    ).count()

    return {
        'ui_rh': request.user.groups.filter(name='RH').exists(),
        'ui_admin': request.user.groups.filter(name='Administrador').exists() or request.user.is_superuser,
        'notificacoes': notificacoes,
        'total_nao_lidas': total_nao_lidas,
    }