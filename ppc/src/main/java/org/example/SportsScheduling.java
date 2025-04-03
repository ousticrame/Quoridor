package org.example;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.BoolVar;

public class SportsScheduling {
    public static void main(String[] args) {
        // Paramètres du problème
        int n = 4;                       // nombre d'équipes (doit être pair pour éviter les journées sans match)
        int rounds = n - 1;              // nombre de journées (round-robin simple : n-1 journées)
        int maxConsecutiveAway = 2;      // contrainte: max 2 matchs consécutifs à l'extérieur par équipe

        Model model = new Model("Calendrier sportif avec contrainte maxConsecutiveAway");
        // Variables :
        // O[i][j] = adversaire de l'équipe i à la journée j (valeurs de 0 à n-1, i exclu)
        IntVar[][] O = new IntVar[n][rounds];
        // P[i][j] = 1 si l'équipe i joue à domicile à la journée j, 0 si elle joue à l'extérieur
        BoolVar[][] P = model.boolVarMatrix("P", n, rounds);

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < rounds; j++) {
                O[i][j] = model.intVar("O_" + i + "_" + j, 0, n - 1, false);
                model.arithm(O[i][j], "!=", i).post();  // une équipe ne peut pas s’affronter elle-même
            }
            // Contrainte: chaque équipe i rencontre chaque autre équipe une seule fois (opposants tous différents)
            model.allDifferent(O[i]).post();
        }

        // Contraintes de cohérence: si l’équipe i affronte l’équipe k en journée j,
        // alors l’équipe k affronte i en j ET l’une joue à domicile pendant que l’autre joue à l’extérieur.
        for (int j = 0; j < rounds; j++) {
            for (int i = 0; i < n; i++) {
                for (int k = i + 1; k < n; k++) {
                    // Si i joue contre k en j...
                    model.ifThen(
                            model.arithm(O[i][j], "=", k),
                            model.arithm(O[k][j], "=", i)    // ...alors k joue contre i en j (symétrie de l'opposition)
                    );
                    model.ifThen(
                            model.arithm(O[i][j], "=", k),
                            model.arithm(P[i][j], "!=", P[k][j])  // ...et l'un des deux est à domicile, l'autre à l'extérieur
                    );
                    // (Contrainte symétrique) Si k joue contre i en j...
                    model.ifThen(
                            model.arithm(O[k][j], "=", i),
                            model.arithm(O[i][j], "=", k)    // ...alors i joue contre k en j
                    );
                    model.ifThen(
                            model.arithm(O[k][j], "=", i),
                            model.arithm(P[i][j], "!=", P[k][j])  // ...et lieux inversés entre i et k
                    );
                }
            }
        }

        // Variables de break : B[i][j] = 1 si l'équipe i a deux matchs de suite sur le même lieu entre journées j et j+1
        BoolVar[][] B = new BoolVar[n][rounds - 1];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < rounds - 1; j++) {
                B[i][j] = model.boolVar("B_" + i + "_" + j);
                // B[i][j] = 1 ssi P[i][j] == P[i][j+1] (deux matchs consécutifs à domicile ou à l'extérieur)
                model.arithm(P[i][j], "=", P[i][j + 1]).reifyWith(B[i][j]);
            }
        }
        // Limitation du nombre total de breaks (toutes équipes confondues) – par exemple n-2 breaks minimum théoriquement
        int maxTotalBreaks = n - 2;
        IntVar totalBreaks = model.intVar("totalBreaks", 0, n * (rounds - 1));
        // totalBreaks = somme de tous les breaks B[i][j]
        model.sum(flatten(B), "=", totalBreaks).post();
        model.arithm(totalBreaks, "<=", maxTotalBreaks).post();

        // ** Nouvelle contrainte ** : limitation des matchs consécutifs à l'extérieur pour chaque équipe.
        // Aucune équipe ne doit jouer plus de `maxConsecutiveAway` matchs de suite à l'extérieur.
        // Cela équivaut à imposer qu'au moins un match à domicile apparaisse dans toute fenêtre de maxConsecutiveAway+1 matchs.
        for (int i = 0; i < n; i++) {
            for (int j = 0; j <= rounds - (maxConsecutiveAway + 1); j++) {
                // Fenêtre de matchs j à j+maxConsecutiveAway pour l'équipe i
                IntVar[] window = new IntVar[maxConsecutiveAway + 1];
                for (int k = 0; k <= maxConsecutiveAway; k++) {
                    window[k] = P[i][j + k];
                }
                // Au moins un 1 (domicile) dans cette fenêtre: somme(P[i][j..j+K]) >= 1 
                model.sum(window, ">=", 1).post();
            }
        }

        // Résolution du modèle
        if (model.getSolver().solve()) {
            System.out.println("Solution trouvée avec contrainte maxConsecutiveAway = " + maxConsecutiveAway);
            // Affichage du calendrier : pour chaque équipe, liste des adversaires avec + (domicile) ou - (extérieur)
            for (int i = 0; i < n; i++) {
                System.out.print("Équipe " + (i + 1) + " : ");
                for (int j = 0; j < rounds; j++) {
                    int opponent = O[i][j].getValue() + 1;          // adversaire (1-indexé pour affichage)
                    boolean home = P[i][j].getValue() == 1;
                    String sign = home ? "+" : "-";                // '+' = match à domicile, '-' = à l'extérieur
                    System.out.print(sign + opponent + "  ");
                }
                System.out.println();
            }
        } else {
            System.out.println("Pas de solution satisfaisant toutes les contraintes.");
        }
    }

    // Fonction utilitaire pour aplatir un tableau 2D de BoolVar en tableau 1D d'IntVar
    private static IntVar[] flatten(BoolVar[][] matrix) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        IntVar[] flat = new IntVar[rows * cols];
        int index = 0;
        for (BoolVar[] row : matrix) {
            for (BoolVar v : row) {
                flat[index++] = v;
            }
        }
        return flat;
    }
}