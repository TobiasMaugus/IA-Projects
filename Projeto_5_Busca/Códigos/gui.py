"""Interface gráfica (tkinter) do Jogo dos Oito.

Executar: python gui.py

- Clique em uma peça adjacente ao espaço vazio para jogar manualmente.
- "Novo Jogo": sorteia um novo estado inicial resolvível.
- "Embaralhar Estado": embaralha o estado atual com movimentos válidos.
- "Resolver com BFS" / "Resolver com A*": calcula a solução; use "Anterior" e
  "Próximo" para percorrer o histórico de passos.
"""
import tkinter as tk
from tkinter import messagebox

from puzzle import Jogo, OBJETIVO

COR_FUNDO = "#F4F1EA"
COR_PECA = "#0F3D3E"
COR_VAZIO = "#DCD6C8"
COR_DESTAQUE = "#E07A3F"
FONTE_PECA = ("Helvetica", 28, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jogo dos Oito — BFS vs A*")
        self.configure(bg=COR_FUNDO, padx=16, pady=16)
        self.resizable(False, False)
        self.jogo = Jogo()
        self.info = ""
        self._montar()
        self._atualizar()

    # ------------------------------------------------------------------ layout
    def _montar(self):
        tabuleiro = tk.Frame(self, bg=COR_FUNDO)
        tabuleiro.grid(row=0, column=0, rowspan=2, padx=(0, 16))
        self.botoes = []
        for i in range(9):
            b = tk.Button(tabuleiro, width=4, height=2, font=FONTE_PECA, relief="flat",
                          command=lambda i=i: self._clicar(i))
            b.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.botoes.append(b)

        lateral = tk.Frame(self, bg=COR_FUNDO)
        lateral.grid(row=0, column=1, sticky="n")
        objetivo = "\n".join(" ".join(str(n) if n else "_" for n in OBJETIVO[r:r + 3])
                             for r in range(0, 9, 3))
        tk.Label(lateral, text="Objetivo:", bg=COR_FUNDO, font=("Helvetica", 10, "bold")).pack(anchor="w")
        tk.Label(lateral, text=objetivo, bg=COR_FUNDO, font=("Courier", 12), justify="left").pack(anchor="w", pady=(0, 10))

        for texto, comando in [("Novo Jogo", self._novo_jogo),
                               ("Embaralhar Estado", self._embaralhar),
                               ("Resolver com BFS", lambda: self._resolver("BFS")),
                               ("Resolver com A*", lambda: self._resolver("A*"))]:
            tk.Button(lateral, text=texto, width=20, command=comando).pack(pady=2)

        nav = tk.Frame(lateral, bg=COR_FUNDO)
        nav.pack(pady=(10, 2))
        self.btn_anterior = tk.Button(nav, text="◀ Anterior", width=9, command=self._anterior)
        self.btn_proximo = tk.Button(nav, text="Próximo ▶", width=9, command=self._proximo)
        self.btn_anterior.grid(row=0, column=0, padx=2)
        self.btn_proximo.grid(row=0, column=1, padx=2)
        self.lbl_passo = tk.Label(lateral, bg=COR_FUNDO, font=("Helvetica", 10))
        self.lbl_passo.pack()

        rodape = tk.Frame(self, bg=COR_FUNDO)
        rodape.grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))
        self.lbl_jogadas = tk.Label(rodape, bg=COR_FUNDO, font=("Helvetica", 11, "bold"))
        self.lbl_jogadas.pack(anchor="w")
        self.lbl_info = tk.Label(rodape, bg=COR_FUNDO, font=("Helvetica", 10), justify="left")
        self.lbl_info.pack(anchor="w")

    # -------------------------------------------------------------- atualização
    def _atualizar(self):
        for i, peca in enumerate(self.jogo.estado):
            self.botoes[i].configure(
                text=str(peca) if peca else "",
                bg=COR_PECA if peca else COR_VAZIO,
                fg="white", activebackground=COR_DESTAQUE)
        j = self.jogo
        self.lbl_jogadas.configure(text=f"Jogadas manuais: {j.jogadas}"
                                   + ("   ✔ Resolvido!" if j.resolvido else ""))
        tem_solucao = j.solucao is not None
        self.btn_anterior.configure(state="normal" if tem_solucao and j.indice > 0 else "disabled")
        self.btn_proximo.configure(state="normal" if tem_solucao and j.indice < j.total_passos else "disabled")
        if tem_solucao:
            movimento = j.solucao.movimentos[j.indice - 1] if j.indice > 0 else "estado inicial"
            self.lbl_passo.configure(text=f"Passo {j.indice}/{j.total_passos} ({movimento})")
        else:
            self.lbl_passo.configure(text="Sem solução calculada")
        self.lbl_info.configure(text=self.info)

    # ------------------------------------------------------------------ eventos
    def _clicar(self, i):
        if self.jogo.clicar(i):
            self.info = ""
            self._atualizar()
            if self.jogo.resolvido:
                messagebox.showinfo("Parabéns!", f"Resolvido em {self.jogo.jogadas} jogadas.")

    def _novo_jogo(self):
        self.jogo.novo_jogo()
        self.info = ""
        self._atualizar()

    def _embaralhar(self):
        self.jogo.embaralhar()
        self.info = ""
        self._atualizar()

    def _resolver(self, metodo):
        if self.jogo.resolvido:
            self.info = "O tabuleiro já está no estado objetivo."
            self._atualizar()
            return
        self.lbl_info.configure(text=f"Resolvendo com {metodo}...")
        self.update_idletasks()
        r = self.jogo.resolver(metodo)
        if not r.encontrado:
            self.info = r.mensagem
            messagebox.showwarning("Sem solução", r.mensagem)
        else:
            self.info = (f"{r.metodo}: {r.passos} passos | {r.nos_expandidos} nós expandidos "
                         f"| {r.tempo:.4f} s")
        self._atualizar()

    def _proximo(self):
        self.jogo.proximo()
        self._atualizar()

    def _anterior(self):
        self.jogo.anterior()
        self._atualizar()


if __name__ == "__main__":
    App().mainloop()
