# Sistema de Exclusão de Emails via Terminal

Este é um sistema CLI (Linha de Comando) simples e eficiente para gerenciar e excluir emails diretamente pelo terminal, utilizando Python.

## Funcionalidades

- Conexão segura via IMAP (Gmail e outros).
- Listagem visual das pastas de email.
- Navegação entre pastas.
- Visualização dos últimos emails.
- Opção para excluir emails específicos.
- Opção para excluir todos os emails de um **REMETENTE específico**.
- Opção para excluir **TODOS** os emails de uma pasta (Limpeza total).
- **Backup Completo**: Baixa todos os emails de uma pasta no formato `.eml` (Preserva anexos e imagens).
- **Restauração**: Faz o upload de arquivos `.eml` de volta para qualquer pasta do servidor.
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

## Visualização do Sistema

Aqui estão alguns exemplos de como o sistema aparece no terminal:

### 1. Menu de Seleção de Pastas
O sistema lista todas as pastas disponíveis na sua conta:
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

### 2. Listagem de Emails
Após selecionar uma pasta, você verá os emails mais recentes:
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

Digite o nome da pasta local para o backup (padrão: backup_INBOX): 
Fazendo backup de 150 emails...
Backup concluído em: backup_INBOX
```

### 4. Backup e Restauração
O sistema agora permite salvaguardar seus emails localmente. O arquivo `.eml` é compatível com a maioria dos clientes de email (Outlook, Thunderbird, Apple Mail).

## Segurança

- Suas credenciais são usadas apenas localmente para conexão direta com o servidor IMAP.
- Recomenda-se o uso de Variáveis de Ambiente ou Senhas de Aplicativo para maior segurança.
