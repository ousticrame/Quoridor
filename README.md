# Solveur

## Solutions explorées

https://github.com/tsionyx/nonogrid

### Implementation naïve

- utilise le backtracking
- mets beaucoup de temps a se rendre compte d'une solution incorrecte
- nombre de cas a testé exponentiel:
  - 2x2: 16 possibilités
  - 4x4: 65536 possibilités

| taille de la grille | nombre de solutions existantes               |
| ------------------- | -------------------------------------------- |
| 2x2                 | 16                                           |
| 4x4                 | 65536                                        |
| 7x7                 | 562949953421312                              |
| 12x12               | 22300745198530623141535718272648361505980416 |

#### Benchmarks

| taille de la grille | temps requis     |
| ------------------- | ---------------- |
| 12x12               | 40ms             |
| 15x15               | 1.1s             |
| 16x16               | 10s              |
| 20x20               | 27h (estimation) |
