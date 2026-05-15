import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(BASE_DIR, "modelo_assedio.pkl")


textos = [
    "meu chefe me humilhou na frente de todos",
    "sou xingado constantemente no trabalho",
    "me perseguem e me isolam da equipe",
    "recebo gritos e ameaças todos os dias",
    "fui constrangido publicamente pelo meu superior",
    "me ridicularizam na frente dos colegas",
    "sofro pressão psicológica e intimidação",
    "me colocam apelidos ofensivos no setor",

    "recebi mensagens com conteúdo sexual",
    "fizeram comentários sobre meu corpo",
    "um colega tentou me tocar sem permissão",
    "recebi cantadas insistentes no trabalho",
    "fui convidada para sair de forma constrangedora",
    "me mandaram fotos íntimas sem consentimento",
    "fizeram insinuações sexuais durante o expediente",
    "me tocaram de forma inadequada",

    "meu chefe ameaçou me demitir se eu não obedecesse",
    "sou obrigado a fazer tarefas fora da minha função",
    "usam o cargo para me pressionar",
    "me deram metas impossíveis como punição",
    "sou forçado a trabalhar além do combinado",
    "meu superior usa a autoridade para me intimidar",
    "estou sofrendo desvio de função",
    "recebo ordens abusivas do meu chefe",
]

rotulos = [
    "moral", "moral", "moral", "moral", "moral", "moral", "moral", "moral",
    "sexual", "sexual", "sexual", "sexual", "sexual", "sexual", "sexual", "sexual",
    "abuso", "abuso", "abuso", "abuso", "abuso", "abuso", "abuso", "abuso",
]


modelo = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classificador", MultinomialNB()),
])

modelo.fit(textos, rotulos)

joblib.dump(modelo, MODELO_PATH)

print("Modelo treinado e salvo em:", MODELO_PATH)