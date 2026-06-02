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

    pedido = "geral"

    if "pedido do usuário:" in contexto_lower and "conversa:" in contexto_lower:
        pedido = contexto_lower.split("pedido do usuário:")[1].split("conversa:")[0].strip()

    tipo = "não identificado"
    status = "não informado"
    gravidade = "não informada"
    resumo = ""
    descricao = ""

    for linha in contexto.splitlines():
        linha_limpa = linha.strip()

        if linha_limpa.startswith("Tipo:"):
            tipo = linha_limpa.replace("Tipo:", "").strip()

        elif linha_limpa.startswith("Status:"):
            status = linha_limpa.replace("Status:", "").strip()

        elif linha_limpa.startswith("Gravidade:"):
            gravidade = linha_limpa.replace("Gravidade:", "").strip()

        elif linha_limpa.startswith("Resumo IA:"):
            resumo = linha_limpa.replace("Resumo IA:", "").strip()

        elif linha_limpa.startswith("Descrição:"):
            descricao = linha_limpa.replace("Descrição:", "").strip()

    texto_base = resumo if resumo and resumo.lower() != "sem resumo" else descricao

    if not texto_base:
        texto_base = "não há informações suficientes no relato."

    mensagens = []

    capturando = False

    for linha in contexto.splitlines():
        linha_limpa = linha.strip()

        if linha_limpa == "CONVERSA:":
            capturando = True
            continue

        if capturando:
            if linha_limpa and not linha_limpa.startswith("["):
                mensagens.append(linha_limpa)

    ultimas_mensagens = mensagens[-4:]

    if pedido == "resumir":
        if ultimas_mensagens:
            return (
                f"Resumo da conversa: esta denúncia é do tipo {tipo}, "
                f"está com status {status} e gravidade {gravidade}. "
                f"O ponto principal registrado é: {texto_base}. "
                f"Nas mensagens recentes, foram mencionados: {' '.join(ultimas_mensagens)}"
            )

        return (
            f"Resumo da denúncia: caso do tipo {tipo}, "
            f"com status {status} e gravidade {gravidade}. "
            f"Relato principal: {texto_base}"
        )

    if pedido == "explicar":
        return (
            f"Explicação da denúncia: este caso foi identificado como {tipo}. "
            f"Isso significa que o relato pode envolver uma situação relacionada a essa categoria. "
            f"O conteúdo principal informado foi: {texto_base}. "
            f"No momento, o status é {status} e a gravidade indicada é {gravidade}. "
            f"A análise final deve ser feita pelo RH."
        )

    if pedido == "sugerir_resposta":
        return (
            "Sugestão de resposta do RH: Olá, sua denúncia foi recebida e analisada com atenção. "
            "As informações relatadas serão tratadas com sigilo, responsabilidade e respeito. "
            "Caso você tenha novas evidências, detalhes adicionais ou dúvidas sobre o acompanhamento, "
            "pode continuar utilizando este chat para complementar as informações."
        )

    if pedido == "proximos_passos":
        return (
            "Próximos passos sugeridos: o RH deve revisar o relato, verificar anexos e links enviados, "
            "avaliar a gravidade do caso e manter o acompanhamento pelo chat. "
            "O funcionário pode complementar a denúncia com datas, nomes, testemunhas ou evidências, se existirem."
        )

    return (
        f"A denúncia está registrada como {tipo}, com status {status}. "
        f"O conteúdo principal informado foi: {texto_base}. "
        f"O caso deve continuar sendo acompanhado pelo RH."
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

   