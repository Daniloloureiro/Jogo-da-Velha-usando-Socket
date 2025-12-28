import socket
import threading
import sys
import time

def servidor_jogo_da_velha():
    print("[1] Criando Socket do Servidor...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    HOST = '0.0.0.0'
    PORT = 9999
    
    try:
        server.bind((HOST, PORT))
    except OSError as e:
        print(f"Erro no Bind (tente 'fuser -k 9999/tcp'): {e}")
        return

    server.listen(2)
    print(f"[2] Servidor rodando na porta {PORT}. Aguardando jogadores...")

    jogadores = []

    # Aceitar Jogador 1
    conn1, addr1 = server.accept()
    jogadores.append(conn1)
    print(f"[3] Jogador 1 conectado: {addr1}")
    # Envia com \n
    conn1.send("AGUARDE|Voce e o X. Aguardando oponente...\n".encode())

    # Aceitar Jogador 2
    conn2, addr2 = server.accept()
    jogadores.append(conn2)
    print(f"[4] Jogador 2 conectado: {addr2}")
    
    # Envia INICIO com \n
    jogadores[0].send("INICIO|X\n".encode())
    jogadores[1].send("INICIO|O\n".encode())

    tabuleiro = [" "] * 9
    turno = 0
    jogo_ativo = True

    while jogo_ativo:
        # Pequena pausa para garantir que o buffer não entupa (opcional, mas ajuda em localhost)
        time.sleep(0.1)
        
        idx_atual = turno % 2
        idx_espera = (turno + 1) % 2
        
        # Envia Tabuleiro com \n
        tabuleiro_str = "".join(tabuleiro)
        msg_estado = f"TABULEIRO|{tabuleiro_str}\n"
        jogadores[0].send(msg_estado.encode())
        jogadores[1].send(msg_estado.encode())

        # Envia Instruções com \n
        jogadores[idx_atual].send("SUA_VEZ|\n".encode())
        jogadores[idx_espera].send("ESPERE|\n".encode())

        try:
            # Lê jogada (Buffer simples pois a resposta é curta)
            dados = jogadores[idx_atual].recv(1024).decode().strip()
            if not dados: break
            
            # Se vier lixo ou comando vazio
            if not dados.isdigit(): continue

            posicao = int(dados)
            if 0 <= posicao <= 8 and tabuleiro[posicao] == " ":
                simbolo = "X" if idx_atual == 0 else "O"
                tabuleiro[posicao] = simbolo
                
                if verificar_vitoria(tabuleiro, simbolo):
                    msg_fim = f"FIM|O jogador {simbolo} venceu!\n"
                    jogadores[0].send(msg_fim.encode())
                    jogadores[1].send(msg_fim.encode())
                    jogo_ativo = False
                elif " " not in tabuleiro:
                    msg_empate = "FIM|Empate (Deu Velha)!\n"
                    jogadores[0].send(msg_empate.encode())
                    jogadores[1].send(msg_empate.encode())
                    jogo_ativo = False
                elif " " not in tabuleiro:
                    msg_empate = "FIM|O jogo empatou (Deu Velha)!\n"
                    jogadores[0].send(msg_empate.encode())
                    jogadores[1].send(msg_empate.encode())
                    jogo_ativo = False    
                else:
                    turno += 1
        except Exception as e:
            print(f"Erro: {e}")
            break

    print("Encerrando servidor.")
    conn1.close()
    conn2.close()
    server.close()

def verificar_vitoria(t, s):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    return any(t[a]==s and t[b]==s and t[c]==s for a,b,c in wins)

if __name__ == "__main__":
    servidor_jogo_da_velha()