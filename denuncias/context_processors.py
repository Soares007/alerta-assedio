def grupos_usuario(request):
    if not request.user.is_authenticated:
        return {
            'ui_rh': False,
            'ui_admin': False,
        }

    return {
        'ui_rh': request.user.groups.filter(name='RH').exists(),
        'ui_admin': request.user.groups.filter(name='Administrador').exists() or request.user.is_superuser,
    }