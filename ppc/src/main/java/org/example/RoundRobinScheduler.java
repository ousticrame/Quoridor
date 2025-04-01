package org.example;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
// import org.chocosolver.solver.constraints.nary.ExtensionalConstraint;
import org.chocosolver.solver.search.strategy.Search;

public class RoundRobinScheduler {

    public static void run() {
        // Paramètres du tournoi
        int n = 6;  // nombre d'équipes (nombre pair)
        int rounds = n - 1; // nombre de journées
        int matchesPerRound = n / 2; // nombre de matchs par journée

        // Contrainte sur la séquence domicile/extérieur (exemple : pas plus de 2 matchs consécutifs)
        int maxConsecutive = 2;

        // Création du modèle
        Model model = new Model("Calendrier de tournoi Round Robin");

        // Matrices pour représenter les équipes jouant à domicile et à l'extérieur pour chaque match de chaque journée
        IntVar[][] home = new IntVar[rounds][matchesPerRound];
        IntVar[][] away = new IntVar[rounds][matchesPerRound];

        // Déclaration des variables pour chaque match
        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                home[r][m] = model.intVar("home_" + r + "_" + m, 0, n - 1);
                away[r][m] = model.intVar("away_" + r + "_" + m, 0, n - 1);
                // Un match ne peut opposer une équipe à elle-même
                model.arithm(home[r][m], "!=", away[r][m]).post();
            }
        }

        // Contrainte 1 : Chaque équipe doit jouer exactement une fois par journée.
        for (int r = 0; r < rounds; r++) {
            IntVar[] teamsRound = new IntVar[n];
            int idx = 0;
            for (int m = 0; m < matchesPerRound; m++) {
                teamsRound[idx++] = home[r][m];
                teamsRound[idx++] = away[r][m];
            }
            model.allDifferent(teamsRound).post();
        }

        // Contrainte 2 : Chaque paire d'équipes ne doit se rencontrer qu'une seule fois.
        // Pour chaque match de chaque journée, on interdit que le même affrontement (dans un sens ou l'autre) apparaisse plusieurs fois.
        for (int r1 = 0; r1 < rounds; r1++) {
            for (int m1 = 0; m1 < matchesPerRound; m1++) {
                for (int r2 = r1; r2 < rounds; r2++) {
                    int mStart = (r1 == r2) ? m1 + 1 : 0;
                    for (int m2 = mStart; m2 < matchesPerRound; m2++) {
                        // Si home1 vs away1 est le même affrontement que home2 vs away2 (dans un sens ou l'autre), c'est interdit.
                        // On impose donc :
                        // (home[r1][m1] != home[r2][m2] OR home[r1][m1] != away[r2][m2])
                        // OU (away[r1][m1] != home[r2][m2] OR away[r1][m1] != away[r2][m2])
                        // Une formulation classique consiste à modéliser l'exclusivité de l'affrontement.
                        // Ici, pour simplifier, nous pouvons appliquer une contrainte implicite en post-traitant la symétrie ou via des
                        // contraintes redondantes. (Des modèles plus avancés utiliseraient des variables supplémentaires pour
                        // représenter l'appartenance à un match unique.)
                        // [Ce point pourra être raffiné dans une version complète.]
                    }
                }
            }
        }

        // Contrainte 3 : Alternance domicile/extérieur et limitation des matchs consécutifs.
        // Pour chaque équipe, on peut définir un vecteur binaire de taille "rounds" indiquant 1 si l'équipe joue à domicile, 0 sinon.
        // Par exemple, pour l'équipe t, créer homeIndicator[t][r] et relier cette variable aux affectations dans les tableaux "home" et "away".
        // On pourra alors utiliser une contrainte "regular" ou une contrainte de glissement (sliding constraint) pour interdire
        // plus de maxConsecutive 1 ou 0 consécutifs.
        //
        // Exemple schématique pour créer ces indicateurs :
        IntVar[][] homeIndicator = new IntVar[n][rounds];
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                homeIndicator[t][r] = model.intVar("H_" + t + "_" + r, 0, 1);
                // Il faut ensuite relier homeIndicator[t][r] à l'affectation de l'équipe t dans la journée r :
                // Si l'équipe t apparaît dans la liste home[r], alors H[t][r] = 1 ; sinon, H[t][r] = 0.
                // La liaison peut se faire via des contraintes de reification et des contraintes "element".
                // [Implémentation détaillée à compléter selon les besoins.]
            }
        }

        // Pour chaque équipe, on ajoute par exemple une contrainte pour limiter les matchs consécutifs à domicile.
        // Une façon simple (mais moins efficace) est d'imposer pour chaque fenêtre de (maxConsecutive+1) rounds que la somme
        // des homeIndicator soit inférieure ou égale à maxConsecutive.
        for (int t = 0; t < n; t++) {
            for (int r = 0; r <= rounds - (maxConsecutive + 1); r++) {
                IntVar[] window = new IntVar[maxConsecutive + 1];
                for (int k = 0; k < maxConsecutive + 1; k++) {
                    window[k] = homeIndicator[t][r + k];
                }
                model.sum(window, "<=", maxConsecutive).post();
            }
        }

        // (Optionnel) Contrainte sur la disponibilité des stades :
        // Par exemple, si l'équipe t n'est pas disponible pour jouer à domicile en journée r, alors on impose :
        // model.arithm(homeIndicator[t][r], "=", 0).post();

        // Stratégie de recherche (pour améliorer les performances)
        Solver solver = model.getSolver();
        solver.setSearch(Search.intVarSearch(
                // Sélection de la variable la plus contrainte : ici, on retourne simplement la première variable non instanciée.
                (IntVar[] vars) -> {
                    for (IntVar v : vars) {
                        if (!v.isInstantiated()) {
                            return v;
                        }
                    }
                    return vars[0];
                },
                // Sélection de la plus petite valeur possible dans le domaine
                var -> var.getLB(),
                model.retrieveIntVars(true)
        ));

        // Recherche et affichage des solutions
        while (solver.solve()) {
            System.out.println("=== Solution trouvée ===");
            for (int r = 0; r < rounds; r++) {
                System.out.println("Journée " + (r + 1) + " :");
                for (int m = 0; m < matchesPerRound; m++) {
                    System.out.println("  Match : Équipe " + home[r][m].getValue()
                            + " (domicile) vs Équipe " + away[r][m].getValue() + " (extérieur)");
                }
            }
            System.out.println("------------------------");
        }

        if (solver.getSolutionCount() == 0) {
            System.out.println("Aucune solution trouvée.");
        }
    }
}
