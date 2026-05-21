import os
import json
import google.generativeai as genai

from .analisador import analisar_texto, gerar_resumo
from .analisador_links import analisar_link

print("ARQUIVO GEMINI_API FOI CARREGADO")


genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

modelo = genai.GenerativeModel(
    "gemini-2.0-flash"
)


def chamar_gemini(prompt):
    resposta = modelo.generate_content(prompt)

    texto = resposta.text.strip()

    print("RESPOSTA BRUTA GEMINI:")
    print(texto)

    texto = texto.replace("```json", "")
    texto = texto.replace("```", "")
    texto = texto.strip()

    inicio = texto.find("{")
    fim = texto.rfind("}") + 1

    if inicio == -1 or fim == -1:
        raise Exception("Gemini não retornou JSON válido")

    texto_json = texto[inicio:fim]

    print("JSON EXTRAÍDO:")
    print(texto_json)

    return json.loads(texto_json)


def analisar_relato_com_fallback(texto):
    try:
        print("TENTANDO USAR GEMINI PARA ANALISAR RELATO...")

        prompt = f"""
Você é uma IA especializada em RH, assédio e compliance corporativo.

Analise o relato abaixo.

Se o texto for aleatório, sem sentido, muito curto ou insuficiente, classifique como "outros",
com gravidade "baixa", urgente false e confiança baixa.

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

        resultado = chamar_gemini(prompt)
        resultado["origem_ia"] = "gemini"

        print("IA USADA NO RELATO: GEMINI")

        return resultado

    except Exception as erro:
        print("IA USADA NO RELATO: LOCAL")
        print("ERRO GEMINI RELATO:", erro)

        resultado = analisar_texto(texto)
        resultado["origem_ia"] = "local"

        return resultado


def gerar_resumo_com_fallback(texto):
    try:
        print("TENTANDO USAR GEMINI PARA RESUMO...")

        prompt = f"""
Você é uma IA especializada em RH.

Crie um resumo profissional para RH do relato abaixo.

Regras:
- O resumo deve ser curto.
- O resumo deve ser profissional.
- O resumo deve ser claro e objetivo.
- Não repita simplesmente o texto original.
- Se o texto for aleatório, sem sentido, muito curto ou insuficiente, diga que o relato possui informações insuficientes para gerar resumo.
- Não invente fatos que não estejam no relato.

Relato:
{texto}

Retorne APENAS JSON válido:

{{
  "resumo": "texto"
}}
"""

        resultado = chamar_gemini(prompt)

        resumo = resultado.get("resumo")

        print("IA USADA NO RESUMO: GEMINI")

        if resumo:
            return resumo

        return "Relato com informações insuficientes para gerar resumo."

    except Exception as erro:
        print("IA USADA NO RESUMO: LOCAL")
        print("ERRO GEMINI RESUMO:", erro)

        return gerar_resumo(texto)


def analisar_link_com_fallback(link):
    try:
        print("TENTANDO USAR GEMINI PARA ANALISAR LINK...")

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
- extensão de arquivo
- tentativa de parecer site confiável

Link:
{link}

Retorne APENAS JSON válido:

{{
  "status": "seguro | suspeito | perigoso",
  "motivo": "explicação curta"
}}
"""

        resultado = chamar_gemini(prompt)
        resultado["origem_ia"] = "gemini"

        print("IA USADA NO LINK: GEMINI")

        return resultado

    except Exception as erro:
        print("IA USADA NO LINK: LOCAL")
        print("ERRO GEMINI LINK:", erro)

        resultado = analisar_link(link)
        resultado["origem_ia"] = "local"

        return resultado
    
def responder_chat_local(contexto):
        contexto_lower = contexto.lower()

        if "link" in contexto_lower or "site" in contexto_lower:
            return "A IA local identificou que há menção a link ou site. Recomenda-se verificar se o endereço parece confiável antes de abrir."
        if "resposta" in contexto_lower and "rh" in contexto_lower:
            return "A IA local recomenda analisar a resposta do RH com atenção e, se ainda houver dúvidas, continuar a conversa pelo chat."
        if "ameaça" in contexto_lower or "ameaçou" in contexto_lower:
            return "A IA local identificou possível situação de ameaça. É recomendado que o RH avalie o caso com prioridade."
        if "humilhação" in contexto_lower or "humilhou" in contexto_lower:
            return "A IA local identificou possível situação de humilhação ou constrangimento no ambiente de trabalho."
        
        return "A IA local pode ajudar a resumir a situação, esclarecer dúvidas gerais e indicar que o caso deve ser analisado cuidadosamente pelo RH."

    
def responder_chat_com_fallback(contexto):
    try:
        print("TENTANDO USAR GEMINI NO CHAT...")

        prompt = f"""
Você é uma IA assistente de RH em um sistema de denúncias.

Sua função é ajudar de forma neutra, respeitosa e objetiva.

Regras:
- Não tome decisão final.
- Não acuse ninguém.
- Não substitua análise humana do RH.
- Explique de forma clara.
- Se faltar informação, diga que faltam detalhes.
- Seja cuidadosa com temas sensíveis.

Contexto:
{contexto}

Retorne APENAS JSON válido:

{{
  "resposta": "texto da resposta da IA"
}}
"""

        resultado = chamar_gemini(prompt)

        print("IA USADA NO CHAT: GEMINI")

        return resultado.get(
            "resposta",
            "Não consegui gerar uma resposta clara com as informações disponíveis."
        )

    except Exception as erro:
        print("IA USADA NO CHAT: LOCAL")
        print("ERRO GEMINI CHAT:", erro)

        return responder_chat_local(contexto)
    
   