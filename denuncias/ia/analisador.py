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
        return "Relato com informações insuficientes para gerar resumo."

    texto_limpo = " ".join(texto.strip().split())
    texto_lower = texto_limpo.lower()

    letras_unicas = len(set(texto_lower.replace(" ", "")))

    if len(texto_limpo) < 20 or letras_unicas <= 4:
        return "Relato aparenta estar incompleto ou sem informações suficientes para resumo."

    regras_resumo = [
        {
            "palavras": ["obrig", "tarefa pessoal", "fora da função", "fora da minha função", "desvio de função", "sem remuneração"],
            "resumo": "Funcionário relata possível abuso de autoridade envolvendo imposição de tarefa inadequada, pessoal ou fora de sua função."
        },
        {
            "palavras": ["ameaç", "medo", "intimid", "coação", "pressionou", "chantagem"],
            "resumo": "Funcionário relata situação envolvendo ameaça, intimidação, pressão ou medo no ambiente de trabalho."
        },
        {
            "palavras": ["humilh", "xing", "ridicular", "constrang", "gritou", "ofendeu", "exposição"],
            "resumo": "Funcionário relata possível humilhação, constrangimento, ofensa ou exposição no ambiente de trabalho."
        },
        {
            "palavras": ["sexual", "tocou", "corpo", "convite", "insinuação", "assediou", "comentário sobre meu corpo"],
            "resumo": "Funcionário relata possível conduta inadequada de natureza sexual no ambiente de trabalho."
        },
        {
            "palavras": ["discrimin", "preconceito", "racismo", "homofobia", "idade", "religião", "aparência", "deficiência"],
            "resumo": "Funcionário relata possível discriminação, preconceito ou tratamento desigual."
        },
        {
            "palavras": ["agress", "bateu", "empurrou", "violência", "machucou", "sangue"],
            "resumo": "Funcionário relata possível agressão física ou situação de violência."
        },
        {
            "palavras": ["isolado", "isolamento", "deixado de lado", "excluído", "ignorado", "ninguém fala comigo"],
            "resumo": "Funcionário relata possível isolamento, exclusão ou tratamento de indiferença pela equipe."
        },
        {
            "palavras": ["perseguição", "persegue", "marcação", "pega no meu pé", "sempre comigo"],
            "resumo": "Funcionário relata possível perseguição ou tratamento recorrente direcionado contra ele."
        },
    ]

    for regra in regras_resumo:
        if any(palavra in texto_lower for palavra in regra["palavras"]):
            return regra["resumo"]

    frases = texto_limpo.replace("!", ".").replace("?", ".").split(".")

    frases_limpas = [
        frase.strip()
        for frase in frases
        if frase.strip()
    ]

    palavras_importantes = [
        "chefe", "supervisor", "gerente", "colega", "equipe",
        "humilhação", "ameaça", "medo", "obrigou", "assédio",
        "discriminação", "abuso", "violência", "isolado",
        "constrangimento", "perseguição", "xingamento"
    ]

    frases_relevantes = []

    for frase in frases_limpas:
        frase_lower = frase.lower()

        if any(palavra in frase_lower for palavra in palavras_importantes):
            frases_relevantes.append(frase)

    if frases_relevantes:
        resumo = ". ".join(frases_relevantes[:2])
        return resumo + "."

    if len(texto_limpo) <= 120:
        return "Funcionário relata uma situação que precisa ser analisada pelo RH com base nas informações fornecidas."

    return texto_limpo[:180] + "..."