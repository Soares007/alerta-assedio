import os
import json
import google.generativeai as genai

from .analisador import analisar_texto, gerar_resumo
from .analisador_links import analisar_link


genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

modelo = genai.GenerativeModel(
    "gemini-2.0-flash"
)


def chamar_gemini(prompt):
    resposta = modelo.generate_content(prompt)

    texto = resposta.text.strip()

    texto = texto.replace("```json", "")
    texto = texto.replace("```", "")

    return json.loads(texto)


def analisar_relato_com_fallback(texto):
    try:

        prompt = f"""
Você é uma IA especializada em RH, assédio e compliance corporativo.

Analise o relato abaixo.

Relato:
{texto}

Retorne APENAS JSON válido:

{{
  "tipo": "moral | sexual | abuso | discriminacao | ameaca | violencia | outros",
  "titulo": "titulo curto",
  "mensagem": "explicação breve",
  "confianca": numero de 0 a 100,
  "gravidade": "baixa | media | alta | critica",
  "urgente": true ou false
}}
"""

        return chamar_gemini(prompt)

    except Exception:
        return analisar_texto(texto)


def gerar_resumo_com_fallback(texto):
    try:

        prompt = f"""
Crie um resumo profissional para RH do relato abaixo.

O resumo deve:
- ser curto
- profissional
- claro
- objetivo

Relato:
{texto}

Retorne APENAS JSON:

{{
  "resumo": "texto"
}}
"""

        resultado = chamar_gemini(prompt)

        return resultado.get(
            "resumo",
            gerar_resumo(texto)
        )

    except Exception:
        return gerar_resumo(texto)


def analisar_link_com_fallback(link):
    try:

        prompt = f"""
Você é uma IA de segurança corporativa.

Analise se este link parece seguro.

NÃO acesse o link.
Analise apenas:
- domínio
- aparência
- estrutura
- sinais suspeitos
- engenharia social

Link:
{link}

Retorne APENAS JSON:

{{
  "status": "seguro | suspeito | perigoso",
  "motivo": "explicação curta"
}}
"""

        return chamar_gemini(prompt)

    except Exception:
        return analisar_link(link)