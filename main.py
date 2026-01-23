import os
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

def select_folder_ui(service):
    while True:
        with console.status("[bold cyan]Buscando pastas..."):
            folders = service.list_folders()
            
        if not folders:
            console.print("[red]Nenhuma pasta encontrada ou falha ao listar pastas.[/red]")
            return None

        table = Table(title="Pastas Disponíveis")
        table.add_column("Nº", justify="right", style="cyan", no_wrap=True)
        table.add_column("Nome da Pasta", style="magenta")

        for idx, folder in enumerate(folders):
            table.add_row(str(idx + 1), folder)

        console.print(table)
        
        choice = IntPrompt.ask("Selecione uma pasta pelo número (0 para sair)", default=0)
        
        if choice == 0:
            return None
            
        if 1 <= choice <= len(folders):
            selected_folder = folders[choice - 1]
            if service.select_folder(selected_folder):
                return selected_folder
            else:
                console.print(f"[red]Falha ao selecionar pasta: {selected_folder}[/red]")
        else:
            console.print("[red]Seleção inválida.[/red]")

def list_and_delete_emails(service, folder_name):
    while True:
        clear_screen()
        console.rule(f"[bold blue]Pasta: {folder_name}[/bold blue]")
        
        with console.status("[bold cyan]Buscando emails..."):
            # Fetch all emails initially - optimization would be pagination
            # For this CLI, let's fetch last 20 emails
            email_ids = service.search_emails("ALL")
            
        if not email_ids:
            console.print("[yellow]Nenhum email encontrado nesta pasta.[/yellow]")
            Prompt.ask("Pressione Enter para voltar", show_default=False)
            return

        total_emails = len(email_ids)
        rprint(f"Total de emails: {total_emails}")
        
        # Pagination / Limit
        limit = 20
        # Get last 'limit' emails
        page_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
        
        with console.status("[bold cyan]Baixando cabeçalhos..."):
            emails = service.fetch_headers(page_ids)

        table = Table(title=f"Últimos {len(emails)} Emails")
        table.add_column("Nº", justify="right", style="cyan")
        table.add_column("De", style="green")
        table.add_column("Assunto", style="white")
        table.add_column("Data", style="yellow")
        table.add_column("ID", style="dim")

        # Map display index to actual email ID
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
        rprint("[1] Deletar email(s) específico(s) da lista acima")
        rprint("[2] Deletar TODOS os emails DA LISTA ACIMA")
        rprint(f"[3] [bold red]Deletar TODOS os {total_emails} emails desta PASTA[/bold red]")
        rprint("[0] Voltar para lista de pastas")
        
        action =  IntPrompt.ask("Selecione uma ação", choices=["0", "1", "2", "3"])
        
        if action == 0:
            return
        elif action == 1:
            to_delete_str = Prompt.ask("Digite os números dos emails para deletar (separados por vírgula, ex: 1,3,5)")
            try:
                nums = [int(x.strip()) for x in to_delete_str.split(",")]
                ids_to_delete = []
                for n in nums:
                    if n in display_map:
                        ids_to_delete.append(display_map[n])
                
                if not ids_to_delete:
                    console.print("[red]Nenhum email válido selecionado.[/red]")
                    Prompt.ask("Pressione Enter para continuar")
                    continue
                    
                confirm = Confirm.ask(f"Tem certeza que deseja deletar {len(ids_to_delete)} emails?", default=False)
                if confirm:
                    with console.status("Deletando..."):
                        # Ensure we convert back to bytes if needed, but imaplib handles string IDs fine mostly
                        service.delete_emails(ids_to_delete)
                    console.print("[bold green]Emails deletados com sucesso![/bold green]")
                    Prompt.ask("Pressione Enter para atualizar")
                    
            except ValueError:
                console.print("[red]Formato de entrada inválido.[/red]")
                Prompt.ask("Pressione Enter para continuar")
        elif action == 2:
            confirm = Confirm.ask(f"[bold red]AVISO: Isso irá deletar TODOS os {len(emails)} emails exibidos ACIMA. Continuar?[/bold red]", default=False)
            if confirm:
                # Collect IDs from the current page
                ids_to_delete = [e['id'] for e in emails] 
                
                with console.status("Deletando..."):
                     service.delete_emails(ids_to_delete)
                console.print("[bold green]Emails deletados![/bold green]")
                Prompt.ask("Pressione Enter para atualizar")
        elif action == 3:
            confirm = Confirm.ask(f"[bold red]PERIGO: Isso irá limpar a pasta inteira ({total_emails} emails). TEM CERTEZA?[/bold red]", default=False)
            if confirm:
                double_confirm = Confirm.ask(f"[bold red]Confirmação final: Deseja realmente excluir {total_emails} emails?[/bold red]", default=False)
                if double_confirm:
                    with console.status("Deletando TODOS os emails... (Isso pode demorar)"):
                        # email_ids is the list of ALL ids in regex search
                        # imaplib store can handle multiple if joined by comma usually, or loop.
                        # Service delete_emails loops. For large numbers, batching might be better but loop is safer for simple impl.
                        service.delete_emails(email_ids)
                    console.print("[bold green]Todos os emails foram deletados![/bold green]")
                    Prompt.ask("Pressione Enter para atualizar")

def main():
    service = login()
    if not service:
        return

    try:
        while True:
            clear_screen()
            folder_name = select_folder_ui(service)
            if not folder_name:
                break
                
            list_and_delete_emails(service, folder_name)
            
    except KeyboardInterrupt:
        rprint("\n[yellow]Saindo...[/yellow]")
    finally:
        service.close()
        rprint("[blue]Conexão encerrada.[/blue]")

if __name__ == "__main__":
    main()
