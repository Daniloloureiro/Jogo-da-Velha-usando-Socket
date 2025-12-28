# Jogo da Velha Multiplayer via Sockets TCP

Este projeto consiste na implementação de um jogo da velha (Tic-Tac-Toe) multiplayer seguindo a arquitetura **Cliente-Servidor**. A comunicação é realizada através de **Sockets TCP** puros, utilizando a biblioteca padrão do Python, sem o uso de frameworks de alto nível (como HTTP ou Socket.IO), para demonstrar o domínio sobre a Camada de Transporte e Aplicação.

Projeto desenvolvido como requisito avaliativo da disciplina de **Redes de Computadores** da **UFPA**.

## 📋 Funcionalidades

* **Arquitetura Cliente-Servidor:** Um servidor central gerencia o estado do jogo e arbitra as regras.
* 
**Conexão TCP:** Uso do protocolo TCP (`SOCK_STREAM`) para garantir a entrega ordenada e confiável dos dados.


* **Interface Gráfica (GUI):** Cliente desenvolvido com **Tkinter** para uma experiência visual, separando a lógica de rede da camada de apresentação.
* **Multithreading:** Implementação de threads para permitir que a interface gráfica permaneça responsiva enquanto aguarda pacotes da rede.
* **Protocolo de Aplicação Próprio:** Definição de um protocolo de texto customizado para troca de mensagens e estados.

## 🚀 Como Executar

### Pré-requisitos

* Python 3.x instalado.
* Sistema Operacional Linux (recomendado/testado no Ubuntu) ou Windows.
* Não é necessário instalar bibliotecas externas (`pip install` não é necessário).

### Passo a Passo

1. **Inicie o Servidor:**
Abra um terminal e execute o script do servidor. Ele ficará escutando na porta `9999`.
```bash
python3 Servidor.py

```


2. **Inicie o Jogador 1:**
Abra um **novo** terminal e execute o cliente.
```bash
python3 ClienteGUI.py

```


3. **Inicie o Jogador 2:**
Abra um **terceiro** terminal e execute o cliente novamente.
```bash
python3 ClienteGUI.py

```



> **Nota:** O jogo iniciará automaticamente assim que o segundo jogador se conectar.

### 🛠 Solução de Problemas Comuns

Se receber o erro `Address already in use` ao reiniciar o servidor:

```bash
# Mata o processo que está prendendo a porta 9999
fuser -k 9999/tcp

```

## ⚙️ Arquitetura e Protocolo

### Decisões de Projeto

O projeto utiliza uma arquitetura onde o **Cliente é "burro"** (apenas exibe dados e envia inputs) e o **Servidor é a "verdade"** (valida regras, verifica vitória e mantém o tabuleiro). Isso evita trapaças e dessincronização.

### Protocolo de Aplicação

Foi desenvolvido um protocolo de texto baseado em mensagens delimitadas por quebra de linha (`\n`). O formato das mensagens é `COMANDO|PAYLOAD`.

| Comando | Origem | Descrição | Exemplo |
| --- | --- | --- | --- |
| `INICIO` | Servidor | Define o símbolo do jogador (X ou O). | `INICIO |
| `TABULEIRO` | Servidor | Envia o estado atual do grid (9 caracteres). | ` TABULEIRO |
| `SUA_VEZ` | Servidor | Libera o cliente para enviar uma jogada. | `SUA_VEZ |
| `ESPERE` | Servidor | Bloqueia o cliente enquanto o oponente joga. | `ESPERE |
| `FIM` | Servidor | Avisa o término do jogo (Vitória ou Empate). | `FIM |
| `[0-8]` | Cliente | Envia o índice da posição jogada. | `4` (Jogou no centro) |

## 🧠 Desafios e Soluções (Relatório Técnico)

Durante o desenvolvimento, foram enfrentados e solucionados os seguintes desafios técnicos, demonstrando o uso de sockets "na essência":

1. **TCP Stickiness (Concatenação de Pacotes):**
* *Problema:* O TCP é um protocolo de fluxo (*stream*). Comandos enviados rapidamente (ex: `INICIO` seguido de `TABULEIRO`) chegavam ao cliente como uma única string (`INICIO|XTABULEIRO...`), quebrando a lógica de leitura.
* *Solução:* Implementação de um **Buffer** no cliente e uso do delimitador `\n`. O cliente acumula os dados recebidos e só processa quando encontra uma quebra de linha, garantindo a integridade das mensagens.


2. **Bloqueio da Interface Gráfica:**
* *Problema:* A função `socket.recv()` é bloqueante. Se executada na thread principal, ela travava a janela do Tkinter enquanto esperava o oponente.
* *Solução:* Uso da biblioteca `threading`. A comunicação de rede roda em uma *Worker Thread* separada, enquanto a *Main Thread* cuida apenas da renderização da GUI.


3. **Address Already in Use:**
* *Problema:* Ao reiniciar o servidor rapidamente, a porta continuava ocupada pelo Kernel em estado `TIME_WAIT`.
* *Solução:* Configuração do socket com `setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` para permitir reuso imediato da porta.



## 👨‍💻 Autores

* **Danilo Loureiro**

---

*Projeto desenvolvido para a disciplina de Redes de Computadores - UFPA.*
