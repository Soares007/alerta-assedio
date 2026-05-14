# 🛡️ Sistema de Denúncias Corporativas

Sistema web moderno desenvolvido com Django para gerenciamento de denúncias corporativas, assédio e irregularidades internas, com foco em anonimato, segurança, organização e comunicação em tempo real.

---

# 📌 Sobre o Projeto

O projeto foi desenvolvido com o objetivo de criar um ambiente seguro para funcionários realizarem denúncias internas de forma:

- segura
- organizada
- anônima
- rastreável
- moderna

O sistema possui um painel completo para RH e administradores, permitindo acompanhamento das denúncias em tempo real através de um Kanban interativo.

---

# 🚀 Tecnologias Utilizadas

- Python 3
- Django 6
- Django Channels
- WebSockets
- SQLite
- HTML5
- CSS3
- JavaScript
- Kanban Drag & Drop
- Sistema de notificações em tempo real

---

# 🎯 Funcionalidades

## 👤 Funcionário

- Criar denúncias
- Denúncias anônimas
- Escolher ocultar setor
- Upload de anexos
- Envio de links
- Visualizar histórico de denúncias
- Receber notificações em tempo real
- Receber e-mails automáticos
- Acompanhar status da denúncia

---

## 🧑‍💼 RH / Administrador

- Painel Kanban moderno
- Arrastar denúncias entre status
- Filtros avançados
- Paginação
- Responder denúncias
- Alterar status
- Visualizar anexos
- Visualizar setor do funcionário
- Notificações em tempo real
- E-mails automáticos
- Dashboard analítico

---

# 📊 Dashboard

O sistema possui dashboards com:

- total de denúncias
- denúncias por tipo
- denúncias por status
- gráficos
- filtros
- métricas

---

# 🔔 Sistema de Notificações

Sistema completo de notificações utilizando:

- WebSocket
- Django Channels
- Atualização em tempo real
- Som de notificação
- Badge dinâmica
- Sininho interativo
- Notificações persistentes

---

# 🧩 Sistema Kanban

As denúncias são organizadas em:

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
- documentos
- links externos

---

# 🔒 Segurança

- Controle de permissões RBAC
- Login obrigatório
- Separação por grupos
- Funcionário visualiza apenas suas denúncias
- RH possui painel administrativo
- Denúncias anônimas protegidas

---

# 👥 Controle de Usuários

## Funcionário
Acesso apenas às próprias denúncias e dashboard pessoal.

## RH
Gerenciamento completo das denúncias.

## Administrador
Controle total do sistema.

---

# ⚡ Recursos Modernos

- Interface responsiva
- Kanban interativo
- Atualização em tempo real
- Filtros automáticos
- Upload de arquivos
- Dashboard moderno
- Sistema de notificações
- UX focada em usabilidade

---

# 📂 Estrutura do Projeto

```bash
sistema_denuncias/
│
├── config/
├── denuncias/
├── media/
├── static/
├── templates/
├── manage.py
└── requirements.txt