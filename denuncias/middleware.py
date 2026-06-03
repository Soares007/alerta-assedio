from django.shortcuts import redirect
from django.urls import reverse


class TrocaSenhaPrimeiroAcessoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            caminho_atual = request.path

            rotas_liberadas = [
                reverse("trocar_senha_primeiro_acesso"),
                reverse("logout"),
            ]

            if caminho_atual not in rotas_liberadas:
                perfil = getattr(request.user, "perfilusuario", None)

                if perfil and perfil.trocar_senha_primeiro_acesso:
                    return redirect("trocar_senha_primeiro_acesso")

        return self.get_response(request)