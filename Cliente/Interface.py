import socket
import threading
import tkinter as tk
from tkinter import messagebox

class JogoVelhaClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Velha - Sockets TCP")
        self.root.geometry("400x550")
        self.root.resizable(False, False)
        
        # Conexão
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 9999
        self.conectado = False
        self.buffer = ""

        try:
            self.client.connect((self.host, self.port))
            self.conectado = True
        except Exception as e:
            messagebox.showerror("Erro", f"Sem conexão com o servidor: {e}")
            self.root.destroy()
            return

        self.simbolo = "?"
        self.meu_turno = False

        # --- INTERFACE ---
        # Placar
        self.frame_placar = tk.Frame(root, bg="#e0e0e0", pady=10)
        self.frame_placar.pack(fill=tk.X)
        self.lbl_score_x = tk.Label(self.frame_placar, text="JOGADOR X: 0", font=("Arial", 12, "bold"), bg="#e0e0e0", fg="blue")
        self.lbl_score_x.pack(side=tk.LEFT, padx=20)
        self.lbl_score_o = tk.Label(self.frame_placar, text="JOGADOR O: 0", font=("Arial", 12, "bold"), bg="#e0e0e0", fg="red")
        self.lbl_score_o.pack(side=tk.RIGHT, padx=20)

        # Status
        self.lbl_status = tk.Label(root, text="Conectado! Aguardando...", font=("Arial", 14), fg="#333")
        self.lbl_status.pack(pady=20)

        # Tabuleiro
        self.frame_tabuleiro = tk.Frame(root)
        self.frame_tabuleiro.pack()

        self.botoes = []
        for i in range(9):
            btn = tk.Button(self.frame_tabuleiro, text="", font=("Arial", 24, "bold"), 
                            width=5, height=2, bg="#f9f9f9",
                            command=lambda idx=i: self.enviar_jogada(idx))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.botoes.append(btn)

        self.lbl_info = tk.Label(root, text="Jogo TCP/IP", font=("Arial", 10), fg="grey")
        self.lbl_info.pack(side=tk.BOTTOM, pady=10)

        if self.conectado:
            self.thread_escuta = threading.Thread(target=self.ouvir_servidor, daemon=True)
            self.thread_escuta.start()

    def enviar_jogada(self, idx):
        if self.meu_turno and self.botoes[idx]['text'] == "":
            try:
                self.client.send(str(idx).encode())
                self.meu_turno = False 
                self.lbl_status.config(text="Enviando...", fg="orange")
            except: pass

    def ouvir_servidor(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                if not data: break
                self.buffer += data
                
                while "\n" in self.buffer:
                    msg, self.buffer = self.buffer.split("\n", 1)
                    if not msg: continue
                    self.processar_protocolo(msg)
            except: break
        self.root.quit()

    def processar_protocolo(self, msg):
        try:
            partes = msg.split("|")
            cmd = partes[0]
            payload = partes[1] if len(partes) > 1 else ""

            if cmd == "INICIO":
                self.simbolo = payload
                self.root.title(f"Jogo da Velha - Você é {self.simbolo}")
                self.lbl_info.config(text=f"Você joga com: {self.simbolo}")

            elif cmd == "TABULEIRO":
                for i in range(9):
                    char = payload[i]
                    cor = "blue" if char == "X" else ("red" if char == "O" else "black")
                    self.botoes[i].config(text=char if char != " " else "", fg=cor)
                self.root.update()

            elif cmd == "PLACAR":
                pt_x, pt_o = payload.split(",")
                self.lbl_score_x.config(text=f"JOGADOR X: {pt_x}")
                self.lbl_score_o.config(text=f"JOGADOR O: {pt_o}")

            elif cmd == "SUA_VEZ":
                self.meu_turno = True
                self.lbl_status.config(text="SUA VEZ!", fg="green")
                self.ativar_botoes(True)

            elif cmd == "ESPERE":
                self.meu_turno = False
                self.lbl_status.config(text="Vez do Oponente...", fg="red")
                self.ativar_botoes(False)

            elif cmd == "FIM":
                # Apenas avisa quem ganhou, não fecha mais a conexão
                messagebox.showinfo("Fim de Rodada", payload)
            
            # --- NOVO: Limpa o tabuleiro visualmente ---
            elif cmd == "REINICIAR":
                self.lbl_status.config(text="Nova Partida Iniciada!", fg="blue")
                for btn in self.botoes:
                    btn.config(text="", state=tk.NORMAL, bg="#f9f9f9")
                self.ativar_botoes(False) # Trava até saber de quem é a vez

            # --- NOVO: Pergunta se quer continuar ---
            elif cmd == "PERGUNTA":
                resposta = messagebox.askyesno("Revanche", payload)
                if resposta:
                    self.client.send("RESPOSTA|SIM\n".encode())
                    self.lbl_status.config(text="Aguardando oponente aceitar...", fg="orange")
                else:
                    self.client.send("RESPOSTA|NAO\n".encode())
                    self.root.destroy()

            elif cmd == "AGUARDE":
                self.lbl_status.config(text=payload)

        except Exception as e:
            print(f"Erro protocolo: {e}")

    def ativar_botoes(self, estado):
        state = tk.NORMAL if estado else tk.DISABLED
        for btn in self.botoes:
            if btn['text'] == "":
                btn.config(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = JogoVelhaClient(root)
    root.mainloop()