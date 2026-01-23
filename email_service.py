import imaplib
import email
from email.header import decode_header
import datetime

class EmailService:
    def __init__(self):
        self.mail = None
        self.username = None

    def connect(self, server, username, password):
        """Connects to the IMAP server."""
        try:
            self.mail = imaplib.IMAP4_SSL(server)
            self.mail.login(username, password)
            self.username = username
            return True
        except Exception as e:
            print(f"Falha na conexão: {e}")
            return False

    def list_folders(self):
        """Lists available folders on the server."""
        if not self.mail:
            return []
        
        status, folders = self.mail.list()
        if status != "OK":
            return []
            
        folder_names = []
        import re
        # Regex to parse IMAP list response: (flags) "separator" "name" or (flags) separator name
        pattern = re.compile(r'\((?P<flags>[^)]*)\) "(?P<delimiter>[^"]+)" (?P<name>.*)')
        # Fallback for unquoted delimiter or name
        pattern_fallback = re.compile(r'\((?P<flags>[^)]*)\) (?P<delimiter>\S+) (?P<name>.*)')

        for folder in folders:
            # Decode folder name
            decoded_folder = folder.decode('utf-8', 'ignore') if isinstance(folder, bytes) else folder
            
            # Common structure: (Flags) "Delimiter" Name
            # We want to extract Name.
            # Example: (\HasNoChildren) "/" "INBOX"
            # Example: (\HasChildren) "." INBOX
            
            # Split by delimiter first? No, delimiter varies.
            # Let's try splitting by " " or " ".
            
            # Robust approach: 
            # 1. Find the closing parenthesis of flags ')'
            # 2. Find the delimiter (quoted or unquoted)
            # 3. Everything after is the name
            
            try:
                # Find end of flags
                if ')' in decoded_folder:
                    post_flags = decoded_folder.split(')', 1)[1].strip()
                    # post_flags is now like: "." INBOX  or  "/" "INBOX"
                    
                    # Check if next part is quoted delimiter
                    if post_flags.startswith('"'):
                        # Find next quote
                        end_quote = post_flags.find('"', 1)
                        if end_quote != -1:
                            name_part = post_flags[end_quote+1:].strip()
                            # Name part might be quoted
                            if name_part.startswith('"') and name_part.endswith('"'):
                                name = name_part[1:-1]
                            else:
                                name = name_part
                        else:
                             name = post_flags
                    else:
                        # Unquoted delimiter. Usually one char or a token.
                        # Split by first space
                        parts = post_flags.split(' ', 1)
                        if len(parts) > 1:
                            name_part = parts[1].strip()
                            if name_part.startswith('"') and name_part.endswith('"'):
                                name = name_part[1:-1]
                            else:
                                name = name_part
                        else:
                            name = parts[0]
                else:
                    # No flags? Just use the whole string
                    name = decoded_folder
                    
                folder_names.append(name)
            except Exception:
                folder_names.append(decoded_folder) # Fallback
                
        return folder_names

    def select_folder(self, folder_name):
        """Selects a specific folder."""
        if not self.mail:
            return False
            
        status, messages = self.mail.select(f'"{folder_name}"')
        return status == "OK"

    def search_emails(self, criteria="ALL"):
        """Searches for emails in the selected folder."""
        if not self.mail:
            return []
            
        status, messages = self.mail.search(None, criteria)
        if status != "OK":
            return []
            
        return messages[0].split()

    def fetch_headers(self, email_ids):
        """Fetches headers (Subject, From, Date) for a list of email IDs."""
        if not self.mail:
            return []

        emails = []
        # Fetch in batches or individually. For simplicity, individual here but robust apps might batch.
        # Reverse order to show newest first usually desired.
        for e_id in reversed(email_ids):
            try:
                status, msg_data = self.mail.fetch(e_id, "(RFC822.HEADER)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        from_ = msg.get("From")
                        date_ = msg.get("Date")
                        
                        emails.append({
                            "id": e_id.decode(),
                            "subject": subject,
                            "from": from_,
                            "date": date_
                        })
            except Exception as e:
                print(f"Erro ao buscar email {e_id}: {e}")
                
        return emails

    def delete_emails(self, email_ids):
        """Deletes specific emails."""
        if not self.mail:
            return False

        for e_id in email_ids:
            self.mail.store(e_id, "+FLAGS", "\\Deleted")
        
        # Expunge to permanently remove
        self.mail.expunge()
        return True

    def close(self):
        """Closes the connection."""
        if self.mail:
            try:
                self.mail.close()
            except:
                pass
            self.mail.logout()
