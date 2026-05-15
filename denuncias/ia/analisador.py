import os
import joblib


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(BASE_DIR, "modelo_assedio.pkl")


def analisar_texto(texto):
    if not texto or not texto.strip():
        return {
            "tipo": "",
            "titulo": "Relato insuficiente",
            "mensagem": "Escreva mais detalhes para que a IA consiga sugerir uma classificação."
        }

    modelo = joblib.load(MODELO_PATH)

    tipo = modelo.predict([texto])[0]

    probabilidades = modelo.predict_proba([texto])[0]
    classes = modelo.classes_

    confianca = max(probabilidades)
    confianca_percentual = round(confianca * 100, 2)

    explicacoes = {
        "moral": {
            "titulo": "Possível assédio moral",
            "mensagem": "A IA identificou sinais relacionados a humilhação, perseguição, constrangimento ou intimidação."
        },
        "sexual": {
            "titulo": "Possível assédio sexual",
            "mensagem": "A IA identificou sinais relacionados a comentários, insinuações, mensagens ou contatos de natureza sexual."
        },
        "abuso": {
            "titulo": "Possível abuso de poder",
            "mensagem": "A IA identificou sinais relacionados ao uso indevido de autoridade, ameaças, ordens abusivas ou desvio de função."
        },
    }

    resposta = explicacoes.get(tipo, {
        "titulo": "Não identificado com clareza",
        "mensagem": "A IA não conseguiu identificar claramente o tipo de situação."
    })

    return {
        "tipo": tipo,
        "titulo": resposta["titulo"],
        "mensagem": resposta["mensagem"],
        "confianca": confianca_percentual
    }