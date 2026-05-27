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

    if "pedido do usuário:" in contexto_lower:
        pedido = contexto_lower.split("pedido do usuário:")[1].split("conversa:")[0].strip()
    else:
        pedido = "geral"

    tipo = "não identificado"
    status = "não informado"
    gravidade = "não informada"
    resumo = ""
    descricao = ""

    for linha in contexto.splitlines():
        linha_limpa = linha.strip()

        if linha_limpa.startswith("Tipo:"):
            tipo = linha_limpa.replace("Tipo:", "").strip()

        if linha_limpa.startswith("Status:"):
            status = linha_limpa.replace("Status:", "").strip()

        if linha_limpa.startswith("Gravidade:"):
            gravidade = linha_limpa.replace("Gravidade:", "").strip()

        if linha_limpa.startswith("Resumo IA:"):
            resumo = linha_limpa.replace("Resumo IA:", "").strip()

        if linha_limpa.startswith("Descrição:"):
            descricao = linha_limpa.replace("Descrição:", "").strip()

    texto_base = resumo if resumo and resumo != "Sem resumo" else descricao

    mensagens = []

    capturando = False

    for linha in contexto.splitlines():
        linha_limpa = linha.strip()

        if linha_limpa == "CONVERSA:":
            capturando = True
            continue

        if capturando and linha_limpa:
            if not linha_limpa.startswith("["):
                mensagens.append(linha_limpa)

    ultimas_mensagens = mensagens[-5:]

    if pedido == "resumir":
        if ultimas_mensagens:
            return (
                f"Resumo da conversa: a denúncia #{tipo} está com status {status} "
                f"e gravidade {gravidade}. O ponto principal relatado é: {texto_base}. "
                f"Nas mensagens recentes, foram tratados estes pontos: {' '.join(ultimas_mensagens[:3])}"
            )

        return (
            f"Resumo da denúncia: trata-se de uma denúncia do tipo {tipo}, "
            f"com status {status} e gravidade {gravidade}. "
            f"O relato principal é: {texto_base}"
        )

    if pedido == "explicar":
        return (
            f"Esta denúncia foi classificada como {tipo}. "
            f"Pelo conteúdo informado, o caso deve ser analisado considerando o relato principal: {texto_base}. "
            f"A gravidade atual é {gravidade} e o status é {status}. "
            f"A IA não substitui a análise do RH, mas pode ajudar a organizar as informações."
        )

    if pedido == "sugerir_resposta":
        return (
            "Sugestão de resposta para o RH: "
            "Olá, sua denúncia foi recebida e analisada com atenção. "
            "As informações relatadas serão tratadas com sigilo e responsabilidade. "
            "Caso existam novos detalhes, evidências ou dúvidas, você pode continuar utilizando este chat para complementar o acompanhamento."
        )

    if pedido == "proximos_passos":
        return (
            "Próximos passos sugeridos: revisar o relato com atenção, verificar se existem anexos ou links de apoio, "
            "manter a comunicação pelo chat caso faltem informações e registrar qualquer nova evidência relevante. "
            "Se houver risco imediato, o caso deve ser tratado com prioridade pelo RH."
        )

    if "link" in contexto_lower or "site" in contexto_lower:
        return "Há menção a link ou site no contexto. Recomenda-se verificar o alerta de segurança exibido pelo sistema antes de abrir qualquer endereço."

    return (
        f"A denúncia está registrada como {tipo}, com status {status}. "
        f"O conteúdo principal informado foi: {texto_base}. "
        f"O caso deve ser acompanhado com atenção pelo RH e pelas partes envolvidas."
    )

    
def responder_chat_local(contexto):
    contexto_lower = contexto.lower()

    if "link" in contexto_lower or "site" in contexto_lower:
        return "A IA local identificou menção a link ou site. Verifique se o endereço parece confiável antes de abrir."

    if "resposta" in contexto_lower and "rh" in contexto_lower:
        return "A IA local recomenda analisar a resposta do RH com atenção e continuar a conversa caso ainda existam dúvidas."

    if "ameaça" in contexto_lower or "ameaçou" in contexto_lower:
        return "A IA local identificou possível situação de ameaça. Recomenda-se avaliação cuidadosa pelo RH."

    if "humilhação" in contexto_lower or "humilhou" in contexto_lower:
        return "A IA local identificou possível humilhação ou constrangimento no ambiente de trabalho."

    return "A IA local pode ajudar a resumir a situação, esclarecer dúvidas gerais e orientar que o caso seja analisado com cuidado pelo RH."


def responder_chat_com_fallback(contexto):
    try:
        print("TENTANDO USAR GEMINI NO CHAT...")

        prompt = f"""
Você é uma IA assistente de RH em um sistema de denúncias.

Regras:
- Não tome decisão final.
- Não acuse ninguém.
- Não substitua análise humana do RH.
- Seja claro, respeitoso e objetivo.
- Se faltar informação, diga que faltam detalhes.

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
   