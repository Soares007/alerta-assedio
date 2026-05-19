import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(BASE_DIR, "modelo_assedio.pkl")


def analisar_texto(texto):
    if not texto or not texto.strip():
        return {
            "tipo": "",
            "titulo": "Relato insuficiente",
            "mensagem": "Escreva mais detalhes para que a IA consiga sugerir uma classificação.",
            "confianca": 0,
            "gravidade": "baixa",
            "urgente": False,
        }

    modelo = joblib.load(MODELO_PATH)

    tipo = modelo.predict([texto])[0]
    texto_lower = texto.lower()
    
    regras_abuso = [
        "supervisor me obrigou",
        "chefe me obrigou",
        "me obrigou a fazer",
        "tarefa pessoal",
        "sem remuneração",
        "fora da minha função",
        "desvio de função",
        "ameaça de demissão",
        "sob ameaça",
    ]
    
    if any(regra in texto_lower for regra in regras_abuso):
        tipo = "abuso"

    probabilidades = modelo.predict_proba([texto])[0]

    confianca = max(probabilidades)
    confianca_percentual = round(confianca * 100, 2)

    explicacoes = {
        "moral": {
            "titulo": "Possível assédio moral",
            "mensagem": "A IA identificou sinais de humilhação, perseguição, constrangimento ou intimidação.",
        },

        "sexual": {
            "titulo": "Possível assédio sexual",
            "mensagem": "A IA identificou sinais de comentários, insinuações, mensagens ou contatos de natureza sexual.",
        },

        "abuso": {
            "titulo": "Possível abuso de poder",
            "mensagem": "A IA identificou sinais de uso indevido de autoridade, ordens abusivas ou desvio de função.",
        },

        "discriminacao": {
            "titulo": "Possível discriminação",
            "mensagem": "A IA identificou sinais de tratamento desigual, preconceito ou exclusão.",
        },

        "ameaca": {
            "titulo": "Possível ameaça",
            "mensagem": "A IA identificou sinais de intimidação, coação ou ameaça direta.",
        },

        "violencia": {
            "titulo": "Possível violência",
            "mensagem": "A IA identificou sinais de agressão física ou conduta violenta.",
        },

        "outros": {
            "titulo": "Situação não classificada",
            "mensagem": "A IA não encontrou sinais suficientes para classificar com segurança.",
        },
    }

    resposta = explicacoes.get(tipo, {
        "titulo": "Não identificado com clareza",
        "mensagem": "A IA não conseguiu identificar claramente o tipo de situação.",
    })

    texto_lower = texto.lower()

    gravidade = "baixa"
    urgente = False

    palavras_criticas = [
        "morte",
        "vou morrer",
        "me matar",
        "suicídio",
        "arma",
        "faca",
        "agressão",
        "agrediu",
        "sangue",
        "violência",
        "ameaça",
        "ameaçou",
        "medo",
        "desespero",
        "pânico",
        "socorro",
    ]

    palavras_altas = [
        "humilhação constante",
        "ameaça de demissão",
        "perseguição diária",
        "toque sem consentimento",
        "agressivo",
        "coação",
        "intimidação",
        "pressão psicológica",
        "abuso constante",
    ]

    if any(palavra in texto_lower for palavra in palavras_criticas):
        gravidade = "critica"
        urgente = True

    elif any(palavra in texto_lower for palavra in palavras_altas):
        gravidade = "alta"
        urgente = True

    elif tipo in ["sexual", "violencia", "ameaca"]:
        gravidade = "alta"
        urgente = True

    elif tipo in ["moral", "abuso", "discriminacao"]:
        gravidade = "media"

    else:
        gravidade = "baixa"

    return {
        "tipo": tipo,
        "titulo": resposta["titulo"],
        "mensagem": resposta["mensagem"],
        "confianca": confianca_percentual,
        "gravidade": gravidade,
        "urgente": urgente,
    }
    
def gerar_resumo(texto):
    if not texto or not texto.strip():
        return ""

    texto_lower = texto.lower()

    if "obrigou" in texto_lower or "tarefa pessoal" in texto_lower or "fora da minha função" in texto_lower:
        return "Funcionário relata possível abuso de autoridade envolvendo imposição de tarefa inadequada ou fora de sua função."

    if "ameaça" in texto_lower or "ameaçou" in texto_lower or "medo" in texto_lower:
        return "Funcionário relata situação envolvendo ameaça, intimidação ou medo no ambiente de trabalho."

    if "humilhou" in texto_lower or "humilha" in texto_lower or "xingou" in texto_lower:
        return "Funcionário relata possível constrangimento, humilhação ou exposição no ambiente de trabalho."

    if "corpo" in texto_lower or "sexual" in texto_lower or "tocou" in texto_lower:
        return "Funcionário relata possível conduta inadequada de natureza sexual."

    frases = texto.split('.')
    frases_limpas = [frase.strip() for frase in frases if frase.strip()]

    if len(frases_limpas) > 1:
        return frases_limpas[0] + "."

    return "Relato registrado para análise do RH."