# 🛡️ Sistema de Denúncias Corporativas

Sistema web moderno desenvolvido com **Django** para gerenciamento de denúncias corporativas, assédio, irregularidades internas e comunicação segura entre funcionários, RH e administradores.

O projeto possui foco em:

- anonimato
- segurança
- rastreabilidade
- organização
- comunicação em tempo real
- gestão de usuários
- automação por e-mail
- apoio com IA local e integração externa opcional

---

# 📌 Sobre o Projeto

O **Sistema de Denúncias Corporativas** foi criado para oferecer um ambiente seguro onde funcionários possam registrar denúncias internas de forma organizada, sigilosa e acompanhável.

O RH e administradores conseguem acompanhar os relatos por meio de painéis modernos, Kanban, dashboard analítico, notificações em tempo real e comunicação por chat vinculada à denúncia.

O sistema também conta com recursos de automação, como envio de e-mails, recuperação de senha por token, cadastro individual e em massa de funcionários, validação de anexos e análise automatizada de relatos.

---

# 🚀 Tecnologias Utilizadas

- Python 3
- Django 6
- Django Channels
- Daphne / ASGI
- WebSockets
- SQLite em desenvolvimento
- PostgreSQL recomendado para produção
- HTML5
- CSS3
- JavaScript
- Chart.js
- OpenPyXL
- Machine Learning local
- Gemini API como integração opcional
- SMTP para envio de e-mails
- Font Awesome
- Kanban Drag & Drop

---

# 🎯 Funcionalidades

## 👤 Funcionário

- Criar denúncias
- Enviar denúncias anônimas
- Escolher ocultar ou exibir setor
- Anexar múltiplos arquivos
- Enviar links junto com a denúncia
- Visualizar suas próprias denúncias
- Acompanhar status da denúncia
- Ver respostas do RH
- Abrir chat vinculado à denúncia respondida
- Enviar mensagens e anexos no chat
- Receber notificações em tempo real
- Receber notificações por e-mail
- Recuperar senha por e-mail com token
- Trocar senha obrigatoriamente no primeiro acesso
- Login por usuário ou e-mail

---

## 🧑‍💼 RH / Administrador

- Painel Kanban moderno
- Arrastar denúncias entre status
- Alterar status automaticamente via Kanban
- Visualizar todas as denúncias
- Filtrar denúncias por status, tipo, setor e pesquisa
- Responder denúncias
- Arquivar denúncias manualmente
- Arquivamento automático de denúncias resolvidas
- Visualizar denúncias arquivadas
- Visualizar detalhes completos da denúncia
- Visualizar anexos no próprio painel
- Abrir imagens, vídeos, PDFs e áudios em modal ampliado
- Visualizar links com card de segurança
- Receber alertas de links suspeitos ou perigosos
- Usar chat vinculado à denúncia
- Responder denúncia pelo próprio chat
- Alterar status pelo chat
- Arquivar denúncia pelo chat
- Gerenciar funcionários
- Cadastrar funcionário individualmente
- Importar funcionários em massa via Excel
- Gerar senha temporária automaticamente
- Enviar acesso por e-mail
- Resetar senha de funcionário
- Reenviar acesso
- Bloquear e desbloquear funcionário
- Editar dados de funcionário
- Pesquisar funcionários em tempo real
- Filtrar funcionários por setor e status
- Dashboard analítico

---

# 📊 Dashboard

O sistema possui dashboard com indicadores e gráficos, incluindo:

- total de denúncias
- denúncias recebidas
- denúncias em análise
- denúncias resolvidas
- denúncias por tipo
- denúncias por status
- denúncias por setor
- evolução por dia

Os gráficos são exibidos com **Chart.js**.

---

# 🔔 Sistema de Notificações

O sistema possui notificações internas em tempo real com:

- WebSocket
- Django Channels
- badge dinâmica
- sino interativo
- dropdown de notificações
- notificações persistentes
- atualização automática

Também há envio de e-mails para eventos importantes, como:

- nova denúncia recebida
- resposta do RH
- nova mensagem no chat
- criação de usuário
- reset de senha
- recuperação de senha

---

# 📧 Sistema de E-mails

O sistema utiliza SMTP para envio real de e-mails.

Recursos implementados:

- envio de e-mail ao RH quando uma denúncia é criada
- envio de e-mail com descrição da denúncia
- envio de credenciais temporárias ao criar funcionário
- envio de nova senha temporária ao resetar acesso
- recuperação de senha por token
- e-mail HTML profissional para redefinição de senha
- e-mails automáticos reaproveitados em fluxos do sistema

---

# 🔐 Recuperação e Segurança de Senha

O sistema possui recuperação de senha por e-mail usando o mecanismo seguro do Django.

Fluxo:

1. O usuário informa o e-mail.
2. O sistema envia um link com token seguro.
3. O link expira em 30 minutos.
4. O usuário cria uma nova senha.
5. A senha é validada em tempo real.

A tela de criação de senha possui:

- validação ao digitar
- confirmação de senha
- botão de exibir/ocultar senha
- requisitos visuais em vermelho e verde
- botão desabilitado até a senha ser válida

---

# 👥 Gestão de Funcionários

O RH pode gerenciar funcionários pela tela administrativa do sistema.

Funcionalidades:

- listar funcionários
- cadastrar funcionário individualmente
- importar funcionários em massa via Excel
- editar nome, e-mail, setor e status
- resetar senha
- reenviar acesso
- bloquear usuário
- desbloquear usuário
- pesquisar por nome, usuário ou e-mail em tempo real
- filtrar por setor
- filtrar por status

---

# 📥 Importação em Massa

O sistema permite importar funcionários por planilha Excel `.xlsx`.

Modelo da planilha:

| nome | email | setor |
|---|---|---|
| João Silva | joao@empresa.com | RH |
| Maria Souza | maria@empresa.com | Financeiro |
| Carlos Lima | carlos@empresa.com | Produção |

Ao importar, o sistema:

- cria o usuário
- gera senha temporária
- vincula ao grupo Funcionário
- cria ou vincula setor
- marca troca de senha obrigatória
- envia acesso por e-mail
- exibe relatório de sucesso e erro

---

# 🧩 Sistema Kanban

As denúncias são organizadas em colunas:

- 📥 Recebidas
- 🔍 Em análise
- ✅ Resolvidas

O RH pode arrastar os cards entre as colunas para alterar o status automaticamente.

---

# 📎 Sistema de Anexos

O sistema permite anexar:

- imagens
- vídeos
- PDFs
- áudios
- documentos permitidos
- links externos

Os anexos podem ser visualizados sem abrir uma nova página.

Recursos visuais:

- slider/carrossel de anexos
- filtros por tipo de arquivo
- mensagem quando não há arquivo daquele tipo
- modal de ampliação para imagens
- player para vídeos e áudios
- visualização de PDFs
- preview de anexos antes do envio no chat
- botão para remover anexo antes de enviar

---

# 🔗 Análise de Links

Links enviados em denúncias ou no chat podem ser analisados automaticamente.

O sistema classifica links como:

- seguro
- suspeito
- potencialmente perigoso

A análise pode considerar:

- domínio
- presença de HTTPS
- encurtadores
- estrutura suspeita
- extensões perigosas
- tentativa de phishing
- engenharia social

A análise pode usar API externa quando disponível e fallback local quando necessário.

---

# 💬 Chat da Denúncia

Após uma denúncia receber resposta do RH, o funcionário pode abrir um chat vinculado à denúncia.

Recursos do chat:

- mensagens entre funcionário e RH
- anonimato preservado quando necessário
- envio de anexos
- preview de anexos antes do envio
- remover anexo antes de enviar
- enviar com Enter
- quebrar linha com Shift + Enter
- atualização automática sem recarregar página
- notificação do outro lado ao receber mensagem
- análise automática de links enviados
- visualização ampliada de imagens, vídeos, PDFs e áudios

---

# 🧠 Inteligência Artificial

O sistema possui apoio de IA para:

- análise inicial do relato
- classificação do tipo de denúncia
- sugestão de gravidade
- identificação de urgência
- geração de resumo
- análise de links

## IA Local

O sistema possui um modelo local de Machine Learning com treinamento automático.

A IA local aprende com:

- exemplos fixos
- denúncias registradas
- feedbacks/correções do RH

Quando um novo feedback é salvo, o sistema pode treinar novamente o modelo e atualizar o arquivo:

```bash
denuncias/ia/modelo_assedio.pkl
```

## Gemini API

O sistema também pode utilizar Gemini API como camada principal de IA.

Caso a API falhe por erro, limite ou indisponibilidade, o sistema usa automaticamente a IA local como fallback.

---

# 🔒 Segurança

Recursos de segurança implementados:

- login obrigatório
- RBAC por grupos
- grupos de Funcionário, RH e Administrador
- funcionário visualiza apenas suas próprias denúncias
- RH visualiza e gerencia denúncias
- administrador possui controle completo
- denúncias anônimas protegidas
- ocultação de setor
- validação de arquivos no backend
- recuperação de senha por token
- troca obrigatória de senha no primeiro acesso
- bloqueio de usuários
- login por usuário ou e-mail

---

# 👥 Perfis de Acesso

## Funcionário

- cria denúncias
- acompanha suas denúncias
- conversa com RH pelo chat
- recebe notificações
- altera senha

## RH

- gerencia denúncias
- responde denúncias
- gerencia funcionários
- acessa dashboard
- arquiva denúncias
- interage no chat

## Administrador

- possui acesso total ao sistema
- pode atuar como RH
- pode gerenciar usuários e denúncias

---

# ⚡ Recursos Modernos

- interface responsiva
- cards modernos
- dashboard visual
- Kanban interativo
- filtros em tempo real
- pesquisa instantânea
- upload múltiplo
- preview de anexos
- modal de mídia
- notificações em tempo real
- e-mails automáticos
- recuperação de senha por token
- importação via Excel
- login por e-mail ou usuário
- IA local com treinamento automático

---

# 📂 Estrutura do Projeto

```bash
sistema_denuncias/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── denuncias/
│   ├── ia/
│   ├── management/
│   ├── migrations/
│   ├── templates/
│   ├── consumers.py
│   ├── forms.py
│   ├── models.py
│   ├── routing.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
│
├── media/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── README.md
```

# 🧭 Roadmap

Possíveis melhorias futuras:

- logs de auditoria
- painel de setores
- exportação de relatórios
- exportação de funcionários para Excel
- dashboard avançado
- PWA
- push notifications
- controle de permissões por gestor
- armazenamento em nuvem para anexos
- layout único para todos os e-mails
- testes automatizados
- Docker
- CI/CD

---

# 👨‍💻 Autor

Projeto desenvolvido para fins acadêmicos e demonstrativos, com foco em segurança do trabalho, denúncias corporativas, compliance e tecnologia.

---

# 📄 Licença

Este projeto pode ser adaptado conforme a necessidade acadêmica ou interna da organização.
