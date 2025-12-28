import socket
import threading
import tkinter as tk
from tkinter import messagebox

class JogoVelhaClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Velha - Sockets TCP")
        
        # Conexão com Sockets (Mesma lógica "raiz" anterior)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('127.0.0.1', 9999))
        except:
            messagebox.showerror("Erro", "Não foi possível conectar ao servidor.")
            self.root.destroy()
            return

        # Estado do Jogo
        self.simbolo = "?"
        self.meu_turno = False
        self.buffer = "" # Buffer para tratar pacotes TCP grudados

        # --- Interface Gráfica (Tkinter) ---
        
        # Label de Status
        self.lbl_status = tk.Label(root, text="Conectando...", font=("Arial", 12))
        self.lbl_status.pack(pady=10)

        # Frame do Tabuleiro
        self.frame_tabuleiro = tk.Frame(root)
        self.frame_tabuleiro.pack()

        # Botões (Matriz 3x3)
        self.botoes = []
        for i in range(9):
            btn = tk.Button(self.frame_tabuleiro, text="", font=("Arial", 20, "bold"), 
                            width=5, height=2,
                            command=lambda idx=i: self.enviar_jogada(idx))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.botoes.append(btn)

        # Inicia Thread de Escuta (Para não travar a tela)
        self.thread_escuta = threading.Thread(target=self.ouvir_servidor, daemon=True)
        self.thread_escuta.start()

    def enviar_jogada(self, idx):
        # Só envia se for a vez do jogador
        if self.meu_turno and self.botoes[idx]['text'] == "":
            try:
                self.client.send(str(idx).encode())
                self.meu_turno = False # Bloqueia até o servidor confirmar
                self.lbl_status.config(text="Aguardando confirmação...", fg="orange")
            except:
                messagebox.showerror("Erro", "Falha ao enviar jogada.")

    def ouvir_servidor(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                if not data: break
                
                self.buffer += data

                # Tratamento do TCP Stream (Buffer e Split)
                while "\n" in self.buffer:
                    msg, self.buffer = self.buffer.split("\n", 1)
                    if not msg: continue
                    
                    # Atualiza a GUI (precisa ser thread-safe, mas Tkinter lida bem com isso simples)
                    self.processar_comando(msg)

            except Exception as e:
                print(f"Erro na conexão: {e}")
                break
        
        self.root.quit()

    def processar_comando(self, msg):
        # Mesma lógica do protocolo que criamos
        partes = msg.split("|")
        cmd = partes[0]
        payload = partes[1] if len(partes) > 1 else ""

        if cmd == "INICIO":
            self.simbolo = payload
            self.root.title(f"Jogo da Velha - Você é o '{self.simbolo}'")
            self.lbl_status.config(text=f"Conectado! Você joga com {self.simbolo}", fg="blue")

        elif cmd == "TABULEIRO":
            # Payload ex: "X  O X..."
            for i in range(9):
                char = payload[i]
                self.botoes[i].config(text=char if char != " " else "")
        
        elif cmd == "SUA_VEZ":
            self.meu_turno = True
            self.lbl_status.config(text="SUA VEZ! Clique em um espaço.", fg="green")
            self.ativar_botoes(True)

        elif cmd == "ESPERE":
            self.meu_turno = False
            self.lbl_status.config(text="Aguardando oponente...", fg="red")
            self.ativar_botoes(False)

        elif cmd == "FIM":
            messagebox.showinfo("Fim de Jogo", payload)
            self.client.close()
            self.root.quit()

        elif cmd == "AGUARDE":
            self.lbl_status.config(text=payload, fg="grey")

    def ativar_botoes(self, estado):
        # Opcional: Desabilitar botões visualmente quando não for a vez
        state = tk.NORMAL if estado else tk.DISABLED
        for btn in self.botoes:
            if btn['text'] == "": # Só habilita os vazios
                btn.config(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = JogoVelhaClient(root)
    root.mainloop()