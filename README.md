<div align="center">

# 📧 Deletar Email — Gerenciador & Backup IMAP via Terminal

**Ferramenta CLI interativa em Python (`Rich`) para limpeza em massa de caixas de e-mail, exclusão por remetente e backup/restauração local no formato `.eml`.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![IMAP](https://img.shields.io/badge/Protocolo-IMAP4_SSL-brightgreen?style=for-the-badge)](https://github.com/Blastoles/Deletar_Email)
[![Rich CLI](https://img.shields.io/badge/Terminal_UI-Rich-8A2BE2?style=for-the-badge)](https://github.com/Textualize/rich)

[🚀 Funcionalidades](#-funcionalidades) •
[💻 Instalação & Configuração](#-instalação) •
[🖥️ Visualização no Terminal](#️-visualização-do-sistema) •
[🌐 English Summary](#-english-summary)

</div>

---

## 🎯 O Problema que Resolve

Quando uma caixa de e-mail corporativa (Locaweb, KingHost, cPanel, Zimbra, Gmail, Outlook) atinge 100% da cota de armazenamento com milhares de notificações automáticas, newsletters ou alertas antigos, apagar pelo Webmail de 50 em 50 páginas leva horas.

O **Deletar Email** conecta diretamente via protocolo **IMAP**, permitindo:
- **Fazer backup completo** de pastas inteiras em arquivos `.eml` (preservando anexos, cabeçalhos e imagens inline);
- **Restaurar backups `.eml`** para qualquer conta ou pasta IMAP (ótimo para migração de servidores de e-mail);
- **Exterminar milhares de e-mails de um remetente específico** ou limpar pastas inteiras em segundos.

---

## 🚀 Funcionalidades

- 🔒 **Conexão Segura via IMAP**: Compatível com Gmail, Outlook, Locaweb, cPanel/Roundcube, Zimbra e qualquer servidor IMAP.
- 📂 **Navegação Visual de Pastas**: Lista todas as pastas da conta (`INBOX`, `Enviados`, `Spam`, `Lixeira`, pastas customizadas).
- 🎯 **Exclusão por Remetente**: Apaga todos os e-mails recebidos de um endereço específico (ex: `no-reply@sistema.com`).
- 🧹 **Limpeza Total de Pasta**: Esvazia pastas lotadas de uma só vez.
- 💾 **Backup Completo (`.eml`)**: Baixa todos os e-mails de uma pasta para o computador mantendo compatibilidade com Outlook, Thunderbird e Apple Mail.
- 📤 **Restauração (`.eml` -> IMAP)**: Faz upload de arquivos `.eml` locais de volta para qualquer pasta do servidor.
- 🎨 **Interface TUI Colorida**: Construída com a biblioteca `rich` para tabelas e menus legíveis no terminal.

---

## 💻 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/Blastoles/Deletar_Email.git
   cd Deletar_Email
   ```
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate

   pip install -r requirements.txt
   ```

## ⚙️ Configuração

1. Copie o arquivo de exemplo `.env.example` para `.env`:
   ```bash
   copy .env.example .env
   ```
2. Preencha suas credenciais no `.env` (no Gmail, utilize uma **Senha de Aplicativo**):
   ```env
   EMAIL_USER=seu_email@gmail.com
   EMAIL_PASSWORD=sua_senha_de_aplicativo
   IMAP_SERVER=imap.gmail.com
   ```
   > **Nota:** Se o arquivo `.env` não estiver configurado, o sistema solicitará as credenciais de forma interativa ao iniciar.

3. Execute o sistema:
   ```bash
   python main.py
   ```

---

## 🖥️ Visualização do Sistema

### 1. Menu de Seleção de Pastas
```text
                          Pastas Disponíveis                           
 ┌────┬──────────────────────────────────────────────────────────────┐
 │ Nº │ Nome da Pasta                                                │
 ├────┼──────────────────────────────────────────────────────────────┤
 │  1 │ INBOX                                                        │
 │  2 │ [Gmail]/Enviados                                             │
 │  3 │ [Gmail]/Lixeira                                              │
 │  4 │ [Gmail]/Spam                                                 │
 └────┴──────────────────────────────────────────────────────────────┘
Selecione uma pasta pelo número (0 para sair): 
```

### 2. Listagem de E-mails, Limpeza e Backup
```text
                          Últimos 20 Emails                            
 ┌────┬────────────────────────────┬────────────────────────┬─────────┐
 │ Nº │ De                         │ Assunto                │ ID      │
 ├────┼────────────────────────────┼────────────────────────┼─────────┤
 │  1 │ newsletters@example.com    │ Sua atualização diária │ 12345   │
 │  2 │ suporte@servico.com        │ Redefinição de senha   │ 12346   │
 │  3 │ promo@loja.com             │ Oferta imperdível!     │ 12347   │
 └────┴────────────────────────────┴────────────────────────┴─────────┘

Opções:
[1] Deletar email(s) específico(s)
[2] Deletar TODOS os emails DA LISTA ACIMA
[3] Deletar TODOS os emails desta PASTA
[4] Deletar todos os emails de um REMETENTE específico
[5] Fazer BACKUP de todos os emails desta PASTA (.eml)
[6] RESTAURAR backup para esta PASTA
[0] Voltar
Selecione uma ação: 5
```

---

## 🌐 English Summary

**Deletar Email** is an interactive Python CLI utility (powered by `Rich`) for managing, cleaning, backing up, and migrating email accounts over **IMAP**.

- **Bulk Email Cleaner**: Delete all emails from a specific sender or purge entire IMAP folders in seconds.
- **Full `.eml` Backup & Restore**: Download entire IMAP folders locally as standard `.eml` files (preserving attachments and headers) and restore/upload `.eml` backups back to any IMAP server.

---

<div align="center">

Desenvolvido por **[Igor Cezario Pereira (Blastoles)](https://github.com/Blastoles)**

</div>
