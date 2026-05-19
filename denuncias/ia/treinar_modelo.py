import os
import django
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from denuncias.models import FeedbackIA

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(BASE_DIR, "modelo_assedio.pkl")


textos = [
    "meu chefe me humilhou na frente de todos",
    "sou xingado constantemente no trabalho",
    "me perseguem e me isolam da equipe",
    "recebo gritos e ameaças todos os dias",
    "fui constrangido publicamente pelo meu superior",
    "recebi mensagens com conteúdo sexual",
    "fizeram comentários sobre meu corpo",
    "um colega tentou me tocar sem permissão",
    "recebi cantadas insistentes no trabalho",
    "me mandaram fotos íntimas sem consentimento",
    "meu chefe ameaçou me demitir se eu não obedecesse",
    "sou obrigado a fazer tarefas fora da minha função",
    "usam o cargo para me pressionar",
    "me deram metas impossíveis como punição",
    "recebo ordens abusivas do meu chefe",
    "fui tratado diferente por causa da minha cor",
    "fizeram piadas racistas comigo",
    "sou excluído por causa da minha religião",
    "sofRO comentários preconceituosos sobre minha aparência",
    "me discriminam por ser mulher",
    "me ameaçaram fisicamente no trabalho",
    "disseram que iriam me esperar na saída",
    "recebi ameaça direta de um colega",
    "me intimidaram dizendo que algo ruim iria acontecer",
    "fui coagido com ameaça",
    "um colega me empurrou durante o expediente",
    "houve agressão física no setor",
    "fui segurado à força",
    "jogaram objeto em mim",
    "sofri violência dentro da empresa",
    "não sei classificar o que aconteceu",
    "tenho dúvidas sobre uma situação no trabalho",
    "quero registrar uma situação desconfortável",
    "algo aconteceu e preciso de orientação",
    "não sei se isso é assédio",
    "meu supervisor me obrigou a fazer uma tarefa pessoal",
    "me mandaram fazer serviço particular do chefe",
    "fui obrigado a fazer algo fora da minha função sob ameaça",
    "meu chefe exigiu tarefa pessoal sem remuneração",
]

rotulos = [
    "moral",
    "moral",
    "moral",
    "moral",
    "moral",
    "sexual",
    "sexual",
    "sexual",
    "sexual",
    "sexual",
    "abuso",
    "abuso",
    "abuso",
    "abuso",
    "abuso",
    "discriminacao",
    "discriminacao",
    "discriminacao",
    "discriminacao",
    "discriminacao",
    "ameaca",
    "ameaca",
    "ameaca",
    "ameaca",
    "ameaca",
    "violencia",
    "violencia",
    "violencia",
    "violencia",
    "violencia",
    "outros",
    "outros",
    "outros",
    "outros",
    "outros",
    "abuso",
    "abuso",
    "abuso",
    "abuso",
]


feedbacks = FeedbackIA.objects.all()

for feedback in feedbacks:
    textos.append(feedback.texto)
    rotulos.append(feedback.tipo_correto)


modelo = Pipeline(
    [
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("classificador", MultinomialNB()),
    ]
)

modelo.fit(textos, rotulos)

joblib.dump(modelo, MODELO_PATH)

print("Modelo treinado com sucesso!")
print("Total de exemplos:", len(textos))
print("Modelo salvo em:", MODELO_PATH)
