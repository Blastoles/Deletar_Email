import os
import re
import getpass
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich import print as rprint
from dotenv import load_dotenv
from email_service import EmailService

# Load environment variables
load_dotenv()

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_filename(name):
    """Sanitizes strings for safe filenames on Windows."""
    # Remove control characters (non-printable)
    name = "".join(char for char in name if char.isprintable())
    # Remove invalid Windows characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Strip leading/trailing whitespace and dots (problematic on Windows)
    return name.strip().strip('.')[:100]

def login():
    console.print(Panel.fit("Sistema de Exclusão de Emails", style="bold blue"))
    
    server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    email_user = os.getenv("EMAIL_USER")
    
    if not email_user:
        email_user = Prompt.ask("Digite seu email")
    else:
        rprint(f"Usando email do .env: [green]{email_user}[/green]")
        
    password = os.getenv("EMAIL_PASSWORD")
    if not password:
        password = getpass.getpass("Digite sua senha de aplicativo: ")
        
    service = EmailService()
    
    with console.status("[bold green]Conectando ao servidor IMAP..."):
        if service.connect(server, email_user, password):
            console.print("[bold green]Conectado com sucesso![/bold green]")
            return service
        else:
            console.print("[bold red]Falha na conexão. Verifique suas credenciais.[/bold red]")
            return None

def perform_backup(service, folder_name, backup_dir=None, email_ids=None):
    """Lógica central para realizar o backup de uma pasta."""
    if not backup_dir:
        backup_dir = f"backup_{folder_name.replace('/', '_')}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    if email_ids is None:
        email_ids = service.search_emails("ALL")
    
    if not email_ids:
        console.print(f"[yellow]Pasta '{folder_name}' está vazia ou sem emails para backup.[/yellow]")
        return 0

    count = 0
    with console.status(f"[bold cyan]Fazendo backup de {len(email_ids)} emails de '{folder_name}'..."):
        headers = service.fetch_headers(email_ids)
        id_to_subject = {e['id']: e['subject'] for e in headers}
        
        for idx, e_id in enumerate(email_ids):
            e_id_str = e_id.decode()
            subject = id_to_subject.get(e_id_str, "Sem_Assunto")
            filename = sanitize_filename(f"{e_id_str}_{subject}.eml")
            filepath = os.path.join(backup_dir, filename)
            
            if os.path.exists(filepath):
                continue
                
            msg_content = service.fetch_full_email(e_id)
            if msg_content:
                try:
                    with open(filepath, "wb") as f:
                        f.write(msg_content)
                    count += 1
                except OSError as err:
                    console.print(f"[red]Erro ao salvar email {e_id_str}: {err}[/red]")
    
    return count

def perform_restore(service, backup_dir, folder_name):
    """Lógica central para restaurar os emails de uma pasta de backup para o servidor."""
    if not os.path.exists(backup_dir):
        return 0
    
    eml_files = [f for f in os.listdir(backup_dir) if f.endswith(".eml")]
    if not eml_files:
        return 0

    if not service.select_folder(folder_name):
        service.create_folder(folder_name)
    
    count = 0
    with console.status(f"Restaurando {len(eml_files)} emails para '{folder_name}'..."):
        for f in eml_files:
            filepath = os.path.join(backup_dir, f)
            try:
                with open(filepath, "rb") as bf:
                    if service.append_email(folder_name, bf.read()):
                        count += 1
            except Exception as e:
                console.print(f"[red]Erro ao restaurar {f}: {e}[/red]")
    return count

def select_folder_ui(service):
    while True:
        with console.status("[bold cyan]Buscando pastas..."):
            folders = service.list_folders()
            
        if not folders:
            console.print("[red]Nenhuma pasta encontrada ou falha ao listar pastas.[/red]")
        
        table = Table(title="Pastas Disponíveis")
        table.add_column("Nº", justify="right", style="cyan", no_wrap=True)
        table.add_column("Nome da Pasta", style="magenta")

        for idx, folder in enumerate(folders or []):
            table.add_row(str(idx + 1), folder)

        console.print(table)
        
        rprint("\nOutras Opções:")
        rprint("[C] Criar nova pasta")
        rprint("[R] RESTAURAR Backup (Opções avançadas)")
        rprint("[T] Backup TOTAL (Todas as Pastas)")
        rprint("[D] [bold red]APAGAR TUDO (Todas as Pastas)[/bold red]")
        rprint("[0] Sair")
        
        choice = Prompt.ask("Selecione uma opção", default="0").upper()
        
        if choice == "0":
            return None
        
        if choice == "T":
            return "TOTAL_BACKUP"
            
        if choice == "R":
            return "RESTORE_MODE"

        if choice == "D":
            return "DELETE_ALL_MODE"

        if choice == "C":
            new_folder = Prompt.ask("Digite o nome da nova pasta")
            if new_folder:
                if service.create_folder(new_folder):
                    console.print(f"[bold green]Pasta '{new_folder}' criada com sucesso![/bold green]")
                else:
                    console.print(f"[bold red]Falha ao criar pasta '{new_folder}'.[/bold red]")
            continue
            
        try:
            val = int(choice)
            if 1 <= val <= len(folders):
                selected_folder = folders[val - 1]
                if service.select_folder(selected_folder):
                    return selected_folder
                else:
                    console.print(f"[red]Falha ao selecionar pasta: {selected_folder}[/red]")
            else:
                console.print("[red]Seleção inválida.[/red]")
        except ValueError:
            console.print("[red]Entrada inválida.[/red]")

def list_and_delete_emails(service, folder_name):
    while True:
        clear_screen()
        console.rule(f"[bold blue]Pasta: {folder_name}[/bold blue]")
        
        with console.status("[bold cyan]Buscando emails..."):
            email_ids = service.search_emails("ALL")
            
        if not email_ids:
            console.print("[yellow]Nenhum email encontrado nesta pasta.[/yellow]")
            Prompt.ask("Pressione Enter para voltar", show_default=False)
            return

        total_emails = len(email_ids)
        rprint(f"Total de emails: {total_emails}")
        
        limit = 20
        page_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
        
        with console.status("[bold cyan]Baixando cabeçalhos..."):
            emails = service.fetch_headers(page_ids)

        table = Table(title=f"Últimos {len(emails)} Emails")
        table.add_column("Nº", justify="right", style="cyan")
        table.add_column("De", style="green")
        table.add_column("Assunto", style="white")
        table.add_column("Data", style="yellow")
        table.add_column("ID", style="dim")

        display_map = {}
        for idx, email_data in enumerate(emails):
            row_num = idx + 1
            display_map[row_num] = email_data['id']
            table.add_row(
                str(row_num), 
                str(email_data['from'])[:30], 
                str(email_data['subject'])[:50], 
                str(email_data['date'])[:20],
                str(email_data['id'])
            )

        console.print(table)
        
        rprint("\nOpções:")
        rprint("[1] Deletar email(s) específico(s)")
        rprint("[2] Deletar TODOS os emails DA LISTA ACIMA")
        rprint(f"[3] [bold red]Deletar TODOS os {total_emails} emails desta PASTA[/bold red]")
        rprint("[4] Deletar por REMETENTE")
        rprint("[5] Fazer BACKUP desta PASTA (.eml)")
        rprint("[6] RESTAURAR backup nesta PASTA")
        rprint("[0] Voltar")
        
        action =  IntPrompt.ask("Ação", choices=["0", "1", "2", "3", "4", "5", "6"])
        
        if action == 0:
            return
        elif action == 1:
            to_delete_str = Prompt.ask("Números para deletar (separados por vírgula)")
            try:
                nums = [int(x.strip()) for x in to_delete_str.split(",")]
                ids = [display_map[n] for n in nums if n in display_map]
                if ids and Confirm.ask(f"Deletar {len(ids)} emails?", default=False):
                    service.delete_emails(ids)
                    console.print("[green]Deletados![/green]")
            except ValueError: pass
        elif action == 2:
            if Confirm.ask("Deletar emails da lista?", default=False):
                service.delete_emails([e['id'] for e in emails])
        elif action == 3:
            if Confirm.ask(f"Limpar pasta ({total_emails} emails)?", default=False):
                service.delete_emails(email_ids)
        elif action == 4:
            sender = Prompt.ask("Email do remetente")
            if sender:
                ids = service.search_emails(f'FROM "{sender}"')
                if ids and Confirm.ask(f"Deletar {len(ids)} de {sender}?", default=False):
                    service.delete_emails(ids)
        elif action == 5:
            backup_dir = Prompt.ask("Diretório de backup", default=f"backup_{folder_name.replace('/', '_')}")
            count = perform_backup(service, folder_name, backup_dir, email_ids)
            console.print(f"[green]Concluído! {count} emails salvos.[/green]")
            Prompt.ask("Enter para continuar")
        elif action == 6:
            backup_dir = Prompt.ask("Caminho do backup")
            count = perform_restore(service, backup_dir, folder_name)
            console.print(f"[green]Restaurados {count} emails.[/green]")
            Prompt.ask("Enter para continuar")

def restore_backup_ui(service):
    """Interface unificada para restauração de backups (Individual ou em Lote)."""
    local_backups = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith('backup_')]
    
    if not local_backups:
        console.print("[yellow]Nenhum backup 'backup_*' encontrado. Digite o caminho manual.[/yellow]")
        manual_path = Prompt.ask("Caminho da pasta de backup").strip().replace('"', '').replace("'", "")
        if os.path.exists(manual_path):
            suggested = os.path.basename(manual_path).replace("backup_", "")
            dest = Prompt.ask("Pasta de destino", default=suggested)
            count = perform_restore(service, manual_path, dest)
            console.print(f"[green]Restaurados {count} emails.[/green]")
        return

    table = Table(title="Backups Locais Encontrados")
    table.add_column("Nº", justify="right", style="cyan")
    table.add_column("Pasta de Backup", style="green")
    for idx, d in enumerate(local_backups):
        table.add_row(str(idx + 1), d)
    console.print(table)
    
    choice = Prompt.ask("Escolha um número, 'A' para todos, ou digite o caminho", default="A").upper()
    
    backups_to_restore = []
    if choice == "A":
        backups_to_restore = local_backups
    else:
        try:
            val = int(choice)
            if 1 <= val <= len(local_backups):
                backups_to_restore = [local_backups[val - 1]]
            else:
                backups_to_restore = [choice]
        except ValueError:
            backups_to_restore = [choice]

    if not backups_to_restore:
        return

    # Escolher modo de restauração
    mode = Prompt.ask(
        "Modo de restauração", 
        choices=["D", "P"], 
        default="D"
    )
    # D = Direto (backup_INBOX -> INBOX)
    # P = Pasta Pai (backup_INBOX -> backup-igor.INBOX)
    
    parent_name = ""
    if mode == "P":
        parent_name = Prompt.ask("Digite o nome da pasta principal (ex: backup-igor)", default="backup-restaurado")

    total_restored = 0
    for b_dir in backups_to_restore:
        if not os.path.exists(b_dir):
            console.print(f"[red]Pulando (não encontrado): {b_dir}[/red]")
            continue
            
        inner_folder = os.path.basename(b_dir).replace("backup_", "")
        if mode == "D":
            target_folder = inner_folder
        else:
            target_folder = f"{parent_name}.{inner_folder}"
        
        console.rule(f"[bold blue]Restaurando: {b_dir} -> {target_folder}[/bold blue]")
        count = perform_restore(service, b_dir, target_folder)
        total_restored += count
        console.print(f"[green]Pronto: {count} emails restaurados.[/green]")

    console.print(f"\n[bold green]Restauração concluída! Total de {total_restored} emails restaurados.[/bold green]")
    Prompt.ask("Pressione Enter para continuar")

def backup_all_folders_ui(service):
    """Realiza o backup de todas as pastas da conta."""
    with console.status("Buscando pastas..."):
        folders = service.list_folders()
    if not folders: return
    
    if Confirm.ask(f"Deseja fazer backup de TODAS as {len(folders)} pastas?", default=True):
        total_saved = 0
        for folder in folders:
            console.rule(f"[bold blue]Backup: {folder}[/bold blue]")
            if service.select_folder(folder):
                total_saved += perform_backup(service, folder)
        console.print(f"\n[bold green]Backup TOTAL concluído! {total_saved} emails salvos.[/bold green]")
    Prompt.ask("Pressione Enter para continuar")

def delete_all_emails_ui(service):
    """Interface para apagar todos os emails de todas as pastas da conta."""
    with console.status("Buscando pastas..."):
        folders = service.list_folders()
    
    if not folders:
        return

    console.print(Panel(
        "[bold red]ATENÇÃO: ESTA OPERAÇÃO IRÁ APAGAR TODOS OS EMAILS DE TODAS AS PASTAS![/bold red]\n"
        "Isso inclui Inbox, Enviadas, Lixo e qualquer outra pasta personalizada.",
        title="PERIGO",
        border_style="red"
    ))

    confirm1 = Confirm.ask("Tem certeza que deseja apagar TUDO?", default=False)
    if not confirm1:
        return

    confirm2 = Confirm.ask("[bold red]CONFIRMAÇÃO FINAL: Deseja realmente excluir todos os emails da conta?[/bold red]", default=False)
    if not confirm2:
        return

    total_deleted = 0
    for folder in folders:
        console.rule(f"[bold red]Limpando: {folder}[/bold red]")
        if service.select_folder(folder):
            ids = service.search_emails("ALL")
            if ids:
                service.delete_emails(ids)
                total_deleted += len(ids)
                console.print(f"[yellow]Removidos {len(ids)} emails de '{folder}'.[/yellow]")
        else:
            console.print(f"[red]Não foi possível acessar a pasta '{folder}'.[/red]")

    console.print(f"\n[bold green]Limpeza concluída! Total de {total_deleted} emails removidos da conta.[/bold green]")
    Prompt.ask("Pressione Enter para continuar")

def main():
    service = login()
    if not service: return
    try:
        while True:
            clear_screen()
            folder_name = select_folder_ui(service)
            if not folder_name: break
            
            if folder_name == "TOTAL_BACKUP": 
                backup_all_folders_ui(service)
            elif folder_name == "RESTORE_MODE": 
                restore_backup_ui(service)
            elif folder_name == "DELETE_ALL_MODE":
                delete_all_emails_ui(service)
            else: 
                list_and_delete_emails(service, folder_name)
    except KeyboardInterrupt:
        rprint("\n[yellow]Saindo...[/yellow]")
    finally:
        service.close()
        rprint("[blue]Conexão encerrada.[/blue]")

if __name__ == "__main__":
    main()
