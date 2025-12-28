import socket
import threading
import tkinter as tk
from tkinter import messagebox

class JogoVelhaClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Velha - Sockets TCP")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        
        # --- Configuração de Rede (Sockets "Raiz") ---
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1' # Localhost
        self.port = 9999
        self.conectado = False
        self.buffer = "" # Buffer para acumular dados do TCP

        try:
            self.client.connect((self.host, self.port))
            self.conectado = True
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor em {self.host}:{self.port}\n\nVerifique se o Servidor.py está rodando.")
            self.root.destroy()
            return

        # Estado do Jogo
        self.simbolo = "?"
        self.meu_turno = False

        # --- Interface Gráfica (Tkinter) ---
        
        # Título / Status Superior
        self.lbl_status = tk.Label(root, text="Conectado! Aguardando jogo...", font=("Arial", 14), fg="#333")
        self.lbl_status.pack(pady=20)

        # Frame para centralizar o tabuleiro
        self.frame_tabuleiro = tk.Frame(root)
        self.frame_tabuleiro.pack()

        # Criação dos Botões (Grid 3x3)
        self.botoes = []
        for i in range(9):
            btn = tk.Button(self.frame_tabuleiro, text="", font=("Arial", 24, "bold"), 
                            width=5, height=2, bg="#f0f0f0",
                            command=lambda idx=i: self.enviar_jogada(idx))
            
            # Posiciona na grade (linha 0-2, coluna 0-2)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.botoes.append(btn)

        # Rodapé com instruções
        self.lbl_info = tk.Label(root, text="Aguardando oponente...", font=("Arial", 10), fg="grey")
        self.lbl_info.pack(side=tk.BOTTOM, pady=10)

        # --- Inicia a Thread de Rede ---
        # Daemon=True garante que a thread morre se fechar a janela
        if self.conectado:
            self.thread_escuta = threading.Thread(target=self.ouvir_servidor, daemon=True)
            self.thread_escuta.start()

    def enviar_jogada(self, idx):
        """ Envia o índice (0-8) para o servidor se for a vez do jogador """
        if self.meu_turno and self.botoes[idx]['text'] == "":
            try:
                # Envia apenas o número. O servidor valida a regra.
                self.client.send(str(idx).encode())
                
                # Bloqueia temporariamente para evitar cliques duplos rápidos
                self.meu_turno = False 
                self.lbl_status.config(text="Enviando jogada...", fg="orange")
            except:
                messagebox.showerror("Erro", "Falha ao enviar dados para o servidor.")

    def ouvir_servidor(self):
        """ Loop que roda em paralelo (Thread Secundária) para ler do Socket """
        while True:
            try:
                # Leitura bloqueante (aguarda dados chegarem)
                data = self.client.recv(1024).decode()
                if not data: 
                    break # Conexão fechada pelo servidor
                
                self.buffer += data # Acumula no buffer

                # Processa mensagens completas (terminadas em \n)
                while "\n" in self.buffer:
                    msg, self.buffer = self.buffer.split("\n", 1)
                    
                    if not msg: continue # Ignora linhas vazias
                    
                    # Atualiza a GUI com o comando recebido
                    self.processar_comando(msg)

            except Exception as e:
                print(f"Erro na conexão: {e}")
                break
        
        # Se saiu do loop, fecha a aplicação
        self.root.quit()

    def processar_comando(self, msg):
        """ Interpreta o protocolo de texto 'COMANDO|PAYLOAD' """
        try:
            partes = msg.split("|")
            cmd = partes[0]
            payload = partes[1] if len(partes) > 1 else ""

            if cmd == "INICIO":
                self.simbolo = payload
                self.root.title(f"Jogo da Velha - Jogador {self.simbolo}")
                self.lbl_info.config(text=f"Você está jogando com: {self.simbolo}")

            elif cmd == "TABULEIRO":
                # Atualiza visualmente o tabuleiro ("X  O ...")
                for i in range(9):
                    char = payload[i]
                    self.botoes[i].config(text=char if char != " " else "", 
                                          fg="blue" if char == "X" else "red")
                
                # [CORREÇÃO CRÍTICA] Força o Tkinter a desenhar AGORA.
                # Sem isso, a mensagem de 'FIM' trava a tela antes do último 'X' aparecer.
                self.root.update() 

            elif cmd == "SUA_VEZ":
                self.meu_turno = True
                self.lbl_status.config(text="SUA VEZ! Jogue.", fg="green")
                self.ativar_botoes(True)

            elif cmd == "ESPERE":
                self.meu_turno = False
                self.lbl_status.config(text="Vez do Oponente...", fg="red")
                self.ativar_botoes(False)

            elif cmd == "FIM":
                # Exibe quem ganhou ou se deu empate
                messagebox.showinfo("Fim de Jogo", payload)
                self.client.close()
                self.root.destroy()

            elif cmd == "AGUARDE":
                self.lbl_status.config(text=payload, fg="grey")
        
        except Exception as e:
            print(f"Erro ao processar comando '{msg}': {e}")

    def ativar_botoes(self, estado):
        """ Habilita ou desabilita os botões vazios """
        state = tk.NORMAL if estado else tk.DISABLED
        for btn in self.botoes:
            if btn['text'] == "": # Só mexe nos botões que ainda não foram jogados
                btn.config(state=state)

if __name__ == "__main__":
    # Inicializa o loop principal do Tkinter
    root = tk.Tk()
    app = JogoVelhaClient(root)
    root.mainloop()