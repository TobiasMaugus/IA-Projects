# Jogo dos Oito

Use Python 3 e mantenha os quatro scripts na mesma pasta. Execute os comandos nessa pasta.

- **`gui.py`**: execute para abrir a interface gráfica, jogar manualmente ou resolver o tabuleiro com BFS ou A*. Requer Tkinter.
  ```bash
  python gui.py
  ```

- **`testes_corretude.py`**: execute para verificar as regras do jogo e a corretude das buscas, por exemplo, após alterar o código.
  ```bash
  python testes_corretude.py
  ```

- **`experimentos.py`**: execute para comparar o tempo de execução e os nós expandidos por BFS e A*. Por padrão, testa 50 casos e salva os resultados em `resultados_experimentos.csv`.
  ```bash
  python experimentos.py
  ```
  Para testar menos casos:
  ```bash
  python experimentos.py --casos 10
  ```

- **`puzzle.py`**: contém a lógica do jogo e os algoritmos de busca. É importado pelos outros scripts e não precisa ser executado diretamente.

Os comandos são independentes: não é necessário executar os testes ou os experimentos para abrir o jogo.
