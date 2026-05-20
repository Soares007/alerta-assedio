from urllib.parse import urlparse


def analisar_link(url):
    if not url:
        return {
            "status": "",
            "motivo": ""
        }

    url_lower = url.lower().strip()
    parsed = urlparse(url_lower)
    dominio = parsed.netloc.replace("www.", "")

    encurtadores = [
        "bit.ly",
        "tinyurl.com",
        "shorturl.at",
        "goo.gl",
        "t.co",
        "cutt.ly",
        "is.gd",
        "ow.ly",
    ]

    extensoes_perigosas = [
        ".exe",
        ".bat",
        ".cmd",
        ".scr",
        ".msi",
        ".dll",
        ".jar",
        ".vbs",
        ".ps1",
        ".zip",
        ".rar",
        ".7z",
    ]

    dominios_confiaveis = [
        "google.com",
        "drive.google.com",
        "docs.google.com",
        "youtube.com",
        "youtu.be",
        "onedrive.live.com",
        "dropbox.com",
        "icloud.com",
    ]

    motivos = []
    pontos_risco = 0

    if parsed.scheme != "https":
        pontos_risco += 2
        motivos.append("O link não usa HTTPS.")

    if dominio in encurtadores:
        pontos_risco += 3
        motivos.append("O link usa encurtador, dificultando saber o destino real.")

    if any(url_lower.endswith(ext) for ext in extensoes_perigosas):
        pontos_risco += 4
        motivos.append("O link aponta para um tipo de arquivo potencialmente perigoso.")

    if "@" in url_lower:
        pontos_risco += 3
        motivos.append("O link contém '@', técnica comum para mascarar destinos.")

    if dominio.count("-") >= 2:
        pontos_risco += 1
        motivos.append("O domínio contém muitos hífens.")

    if sum(char.isdigit() for char in dominio) >= 5:
        pontos_risco += 1
        motivos.append("O domínio contém muitos números.")

    if dominio in dominios_confiaveis:
        pontos_risco -= 2
        motivos.append("O domínio está na lista de serviços conhecidos.")

    if pontos_risco >= 4:
        status = "perigoso"
    elif pontos_risco >= 2:
        status = "suspeito"
    else:
        status = "seguro"

    if not motivos:
        motivos.append("Nenhum sinal forte de risco foi identificado.")

    return {
        "status": status,
        "motivo": " ".join(motivos)
    }