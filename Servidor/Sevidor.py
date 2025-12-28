import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import time

class ServidorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor - Monitor de System Calls")
        self.root.geometry("700x600")
        
        # --- Título ---
        self.lbl_titulo = tk.Label(root, text="Monitor de Sockets (Camada de Transporte)", font=("Arial", 12, "bold"))
        self.lbl_titulo.pack(pady=5)

        # --- Área de Log ---
        self.log_area = scrolledtext.ScrolledText(root, font=("Consolas", 10), state='disabled', bg="#1e1e1e", fg="white")
        self.log_area.pack(expand=True, fill='both', padx=10, pady=5)

        # --- Configuração de Cores para destacar as Funções ---
        self.log_area.tag_config("SYSCALL", foreground="#ffff00", font=("Consolas", 10, "bold")) # Amarelo (Funções C/Python)
        self.log_area.tag_config("INFO", foreground="#aaaaaa")       # Cinza
        self.log_area.tag_config("TX", foreground="#00ff00")         # Verde
        self.log_area.tag_config("RX", foreground="#00ccff")         # Azul
        self.log_area.tag_config("ERROR", foreground="#ff5555")      # Vermelho

        self.btn_sair = tk.Button(root, text="Encerrar Servidor", command=self.fechar_servidor, bg="#cc0000", fg="white")
        self.btn_sair.pack(pady=5)

        self.servidor_ativo = True
        self.server_socket = None
        
        # Inicia a Thread principal do servidor (Simulando o processo pai)
        self.thread = threading.Thread(target=self.iniciar_logica_servidor, daemon=True)
        self.thread.start()

    def log(self, mensagem, tag="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{timestamp}] {mensagem}\n", tag)
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def fechar_servidor(self):
        self.servidor_ativo = False
        try:
            if self.server_socket: self.server_socket.close()
        except: pass
        self.root.destroy()

    def iniciar_logica_servidor(self):
        # 1. SOCKET
        self.log(">>> CHAMADA: socket(AF_INET, SOCK_STREAM)", "SYSCALL")
        self.log("    -> Criando descritor de arquivo (File Descriptor)...", "INFO")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Configuração extra (setsockopt)
        self.log(">>> CHAMADA: setsockopt(SOL_SOCKET, SO_REUSEADDR)", "SYSCALL")
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        HOST = '0.0.0.0'
        PORT = 9999
        
        try:
            # 2. BIND
            self.log(f">>> CHAMADA: bind({HOST}, {PORT})", "SYSCALL")
            self.log("    -> Associando IP e Porta ao socket...", "INFO")
            self.server_socket.bind((HOST, PORT))
            
            # 3. LISTEN
            self.log(">>> CHAMADA: listen(2)", "SYSCALL")
            self.log("    -> Entrando em modo passivo (Fila=2)...", "INFO")
            self.server_socket.listen(2)
            
        except OSError as e:
            self.log(f"ERRO CRÍTICO: {e}", "ERROR")
            return

        jogadores = []
        
        # Aceitando Jogador 1
        self.log(">>> CHAMADA: accept() [Bloqueante]", "SYSCALL")
        self.log("    -> Processo suspenso aguardando Jogador 1...", "INFO")
        
        conn1, addr1 = self.server_socket.accept() # Bloqueia aqui
        
        self.log(f"<<< RETORNO: accept() -> Conexão de {addr1}", "SYSCALL")
        jogadores.append(conn1)
        self.enviar_pacote(conn1, "AGUARDE|Aguardando oponente...\n", "Jog1")

        # Aceitando Jogador 2
        self.log(">>> CHAMADA: accept() [Bloqueante]", "SYSCALL")
        self.log("    -> Aguardando Jogador 2...", "INFO")
        
        conn2, addr2 = self.server_socket.accept() # Bloqueia aqui
        
        self.log(f"<<< RETORNO: accept() -> Conexão de {addr2}", "SYSCALL")
        jogadores.append(conn2)
        
        # Inicio da lógica de "Fork/Thread" para gerenciar a sessão
        self.log(">>> SISTEMA: Iniciando Thread de Jogo (Simulando Fork)", "SYSCALL")
        
        # Setup inicial
        self.enviar_pacote(jogadores[0], "INICIO|X\n", "Jog1")
        self.enviar_pacote(jogadores[1], "INICIO|O\n", "Jog2")
        placar = {"X": 0, "O": 0}

        # Loop Principal
        while self.servidor_ativo:
            tabuleiro = [" "] * 9
            turno = 0
            jogo_ativo = True
            
            self.log("--- ESTADO: Nova Partida Iniciada ---", "INFO")
            self.enviar_pacote(jogadores[0], "REINICIAR|\n", "Jog1")
            self.enviar_pacote(jogadores[1], "REINICIAR|\n", "Jog2")

            while jogo_ativo:
                time.sleep(0.05)
                idx = turno % 2
                oponente = (turno + 1) % 2
                
                # Estado e Permissão
                tab_msg = f"TABULEIRO|{''.join(tabuleiro)}\n"
                # (Opcional: não logar o tabuleiro toda vez pra não poluir, ou logar como INFO)
                try:
                    jogadores[0].send(tab_msg.encode())
                    jogadores[1].send(tab_msg.encode())
                except: pass

                self.enviar_pacote(jogadores[idx], "SUA_VEZ|\n", f"Jog{idx+1}")
                self.enviar_pacote(jogadores[oponente], "ESPERE|\n", f"Jog{oponente+1}")

                try:
                    # 4. RECV (Leitura)
                    self.log(f">>> CHAMADA: recv() [Aguardando Jog{idx+1}]", "SYSCALL")
                    dados = jogadores[idx].recv(1024).decode().strip()
                    
                    if not dados:
                        self.log("<<< RETORNO: recv() -> Vazio (FIN recebido)", "SYSCALL")
                        self.servidor_ativo = False
                        break
                    
                    self.log(f"<<< RETORNO: recv() -> '{dados}'", "RX")
                    
                    if not dados.isdigit(): continue
                    pos = int(dados)

                    if 0 <= pos <= 8 and tabuleiro[pos] == " ":
                        simbolo = "X" if idx == 0 else "O"
                        tabuleiro[pos] = simbolo
                        
                        vencedor = None
                        if self.verificar_vitoria(tabuleiro, simbolo):
                            vencedor = simbolo
                            placar[simbolo] += 1
                            msg_fim = f"FIM|Vitoria de {simbolo}!\n"
                        elif " " not in tabuleiro:
                            vencedor = "Empate"
                            msg_fim = "FIM|Empate!\n"

                        if vencedor:
                            # Envia Placar Atualizado
                            msg_placar = f"PLACAR|{placar['X']},{placar['O']}\n"
                            self.enviar_pacote(jogadores[0], msg_placar, "Jog1")
                            self.enviar_pacote(jogadores[1], msg_placar, "Jog2")
                            
                            self.enviar_pacote(jogadores[0], msg_fim, "Jog1")
                            self.enviar_pacote(jogadores[1], msg_fim, "Jog2")
                            jogo_ativo = False
                        else:
                            turno += 1

                except Exception as e:
                    self.log(f"ERRO: {e}", "ERROR")
                    self.servidor_ativo = False
                    break

            # Revanche
            if self.servidor_ativo:
                self.enviar_pacote(jogadores[0], "PERGUNTA|Jogar dnv?\n", "Jog1")
                self.enviar_pacote(jogadores[1], "PERGUNTA|Jogar dnv?\n", "Jog2")
                try:
                    self.log(">>> CHAMADA: recv() [Esperando Respostas]", "SYSCALL")
                    r1 = jogadores[0].recv(1024).decode()
                    r2 = jogadores[1].recv(1024).decode()
                    if "SIM" in r1 and "SIM" in r2:
                        self.log("--- Revanche Aceita ---", "INFO")
                    else:
                        self.servidor_ativo = False
                except: self.servidor_ativo = False

        self.log(">>> CHAMADA: close() - Encerrando sockets", "SYSCALL")
        try:
            jogadores[0].close()
            jogadores[1].close()
        except: pass
        self.server_socket.close()

    def enviar_pacote(self, socket_cliente, msg, nome):
        try:
            # 5. SEND
            # self.log(f">>> CHAMADA: send() -> {nome}", "SYSCALL") # Opcional: Descomente se quiser muito detalhe
            socket_cliente.send(msg.encode())
            msg_clean = msg.replace("\n", "")
            if "TABULEIRO" not in msg: # Filtra para não poluir
                self.log(f"TX -> {nome}: {msg_clean}", "TX")
        except: pass

    def verificar_vitoria(self, t, s):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(t[a]==s and t[b]==s and t[c]==s for a,b,c in wins)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorGUI(root)
    root.mainloop()