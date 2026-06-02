import os
import joblib

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from denuncias.models import Denuncia, FeedbackIA


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(BASE_DIR, "modelo_assedio.pkl")


EXEMPLOS_FIXOS = [
    ("meu chefe me humilhou na frente de todos", "moral"),
    ("fui xingado e constrangido no trabalho", "moral"),
    ("fui exposto na frente da equipe", "moral"),
    ("me chamaram de incompetente na frente dos colegas", "moral"),

    ("recebi comentários sexuais indesejados", "sexual"),
    ("tocaram no meu corpo sem permissão", "sexual"),
    ("recebi mensagens com conteúdo sexual", "sexual"),
    ("fizeram piadas sobre meu corpo", "sexual"),

    ("meu supervisor me obrigou a fazer tarefa pessoal", "abuso"),
    ("fui obrigado a fazer algo fora da minha função", "abuso"),
    ("me mandaram resolver assunto particular do chefe", "abuso"),
    ("fui ameaçado caso não fizesse tarefa pessoal", "abuso"),

    ("sofri preconceito pela minha aparência", "discriminacao"),
    ("fui tratado diferente por causa da minha religião", "discriminacao"),
    ("sofri discriminação por causa da minha idade", "discriminacao"),
    ("fui excluído por causa da minha deficiência", "discriminacao"),

    ("fui ameaçado de demissão injustamente", "ameaca"),
    ("me ameaçaram no ambiente de trabalho", "ameaca"),
    ("disseram que eu sofreria consequências", "ameaca"),
    ("fui intimidado pelo meu superior", "ameaca"),

    ("um colega me empurrou durante o expediente", "violencia"),
    ("houve agressão física no trabalho", "violencia"),
    ("fui segurado com força durante uma discussão", "violencia"),
    ("um funcionário tentou me agredir", "violencia"),

    ("não sei classificar o ocorrido", "outros"),
    ("quero registrar uma situação desconfortável", "outros"),
    ("aconteceu algo estranho no trabalho", "outros"),
]


def treinar_ia_automaticamente():
    print("\n" + "=" * 60)
    print("INICIANDO TREINAMENTO AUTOMÁTICO DA IA")
    print("=" * 60)

    dados = []

    dados.extend(EXEMPLOS_FIXOS)

    print(f"EXEMPLOS FIXOS CARREGADOS: {len(EXEMPLOS_FIXOS)}")

    feedbacks = FeedbackIA.objects.all()

    print(f"FEEDBACKS ENCONTRADOS: {feedbacks.count()}")

    for feedback in feedbacks:
        if feedback.texto and feedback.tipo_correto:
            dados.append((
                feedback.texto,
                feedback.tipo_correto
            ))

    denuncias = Denuncia.objects.exclude(
        descricao__isnull=True
    ).exclude(
        descricao=""
    )

    print(f"DENÚNCIAS ENCONTRADAS: {denuncias.count()}")

    for denuncia in denuncias:
        if denuncia.tipo and denuncia.descricao:
            dados.append((
                denuncia.descricao,
                denuncia.tipo
            ))

    print(f"TOTAL DE EXEMPLOS PARA TREINAMENTO: {len(dados)}")

    if len(dados) < 10:
        print("TREINAMENTO CANCELADO: MENOS DE 10 EXEMPLOS")
        print("=" * 60 + "\n")
        return False

    textos = [texto for texto, _ in dados]
    rotulos = [rotulo for _, rotulo in dados]

    print(f"TOTAL DE TEXTOS: {len(textos)}")
    print(f"TOTAL DE RÓTULOS: {len(rotulos)}")

    tipos_unicos = sorted(set(rotulos))

    print("TIPOS APRENDIDOS:")
    for tipo in tipos_unicos:
        quantidade = rotulos.count(tipo)
        print(f" - {tipo}: {quantidade}")

    modelo = Pipeline([
        ("vetorizador", CountVectorizer()),
        ("classificador", MultinomialNB())
    ])

    print("TREINANDO MODELO...")

    modelo.fit(textos, rotulos)

    print("MODELO TREINADO COM SUCESSO")

    joblib.dump(modelo, MODELO_PATH)

    print(f"MODELO SALVO EM: {MODELO_PATH}")

    print("=" * 60)
    print("TREINAMENTO FINALIZADO")
    print("=" * 60 + "\n")

    return True