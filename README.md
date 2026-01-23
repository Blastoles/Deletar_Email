# Sistema de Exclusão de Emails via Terminal

Este é um sistema CLI (Linha de Comando) simples e eficiente para gerenciar e excluir emails diretamente pelo terminal, utilizando Python.

## Funcionalidades

- Conexão segura via IMAP (Gmail e outros).
- Listagem visual das pastas de email.
- Navegação entre pastas.
- Visualização dos últimos emails.
- Opção para excluir emails específicos.
- Opção para excluir **TODOS** os emails de uma pasta (Limpeza total).
- Interface bonita e colorida usando a biblioteca `rich`.

## Requisitos

- Python 3.8+
- Conta de email com acesso IMAP habilitado (Para Gmail, necessário usar "Senha de Aplicativo").

## Instalação

1. Clone o repositório ou baixe os arquivos.
2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração

1. Renomeie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   # ou no Windows
   copy .env.example .env
   ```
2. Edite o arquivo `.env` com suas credenciais:
   ```env
   EMAIL_USER=seu_email@gmail.com
   EMAIL_PASSWORD=sua_senha_de_aplicativo
   IMAP_SERVER=imap.gmail.com
   ```
   > **Nota:** Se não configurar o `.env`, o sistema pedirá as credenciais ao iniciar.

## Uso

Execute o arquivo principal:
```bash
python main.py
```

Siga as instruções na tela:
1. Selecione a pasta que deseja gerenciar.
2. Visualize a lista de emails.
3. Escolha uma ação (Deletar específicos, deletar exibidos ou limpar pasta).

## Segurança

- Suas credenciais são usadas apenas localmente para conexão direta com o servidor IMAP.
- Recomenda-se o uso de Variáveis de Ambiente ou Senhas de Aplicativo para maior segurança.
