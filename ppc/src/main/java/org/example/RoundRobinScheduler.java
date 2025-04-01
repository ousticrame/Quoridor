package org.example;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;

public class RoundRobinScheduler {

    public static void run() {
        // Paramètres du tournoi
        int n = 8;  // nombre d'équipes (nombre pair)
        int rounds = n - 1; // nombre de journées
        int matchesPerRound = n / 2; // nombre de matchs par journée

        // Contrainte sur la séquence domicile/extérieur (exemple : pas plus de 2 matchs consécutifs)
        int maxConsecutive = 2;

        // Création du modèle
        Model model = new Model("Calendrier de tournoi Round Robin");

        // Matrices pour représenter les équipes jouant à domicile et à l'extérieur pour chaque match de chaque journée
        IntVar[][] home = new IntVar[rounds][matchesPerRound];
        IntVar[][] away = new IntVar[rounds][matchesPerRound];

        // On va créer une matrice pour encoder la paire (indépendamment de l'ordre)
        IntVar[][] pair = new IntVar[rounds][matchesPerRound];

        // Pour chaque match, on crée les variables et on impose qu'une équipe ne joue pas contre elle-même.
        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                home[r][m] = model.intVar("home_" + r + "_" + m, 0, n - 1);
                away[r][m] = model.intVar("away_" + r + "_" + m, 0, n - 1);
                model.arithm(home[r][m], "!=", away[r][m]).post();

                // Variable pour encoder la paire, domaine : [0, n*n -1]
                pair[r][m] = model.intVar("pair_" + r + "_" + m, 0, n * n - 1);
            }
        }

        // Contrainte 1 : Chaque équipe joue une seule fois par journée.
        for (int r = 0; r < rounds; r++) {
            IntVar[] teamsRound = new IntVar[n];
            int idx = 0;
            for (int m = 0; m < matchesPerRound; m++) {
                teamsRound[idx++] = home[r][m];
                teamsRound[idx++] = away[r][m];
            }
            model.allDifferent(teamsRound).post();
        }

        // Contrainte 2 : Chaque paire d'équipes (peu importe l'ordre) se rencontre une seule fois.
        // Pour cela, on définit pour chaque match deux variables auxiliaires minTeam et maxTeam
        // et on lie la variable "pair" avec la formule : pair = minTeam * n + maxTeam.
        // Ensuite, on impose que l'ensemble de ces "pair" soit allDifferent.
        IntVar[] allPairs = new IntVar[rounds * matchesPerRound];
        int index = 0;
        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                // Variables auxiliaires pour le minimum et le maximum
                IntVar minTeam = model.intVar("min_" + r + "_" + m, 0, n - 1);
                IntVar maxTeam = model.intVar("max_" + r + "_" + m, 0, n - 1);

                // Si home < away alors minTeam = home et maxTeam = away, sinon l'inverse.
                // On utilise ifThenElse pour modéliser ce choix.
                model.ifThenElse(
                        model.arithm(home[r][m], "<", away[r][m]),
                        model.and(
                                model.arithm(minTeam, "=", home[r][m]),
                                model.arithm(maxTeam, "=", away[r][m])
                        ),
                        model.and(
                                model.arithm(minTeam, "=", away[r][m]),
                                model.arithm(maxTeam, "=", home[r][m])
                        )
                );
                // Lier la variable pair à l'expression minTeam * n + maxTeam.
                model.scalar(new IntVar[]{minTeam, maxTeam}, new int[]{n, 1}, "=", pair[r][m]).post();

                allPairs[index++] = pair[r][m];
            }
        }
        model.allDifferent(allPairs).post();

        // Contrainte 3 : Alternance domicile/extérieur pour chaque équipe.
        // Pour simplifier, nous définissons pour chaque équipe et chaque journée un indicateur binaire.
        IntVar[][] homeIndicator = new IntVar[n][rounds];
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                homeIndicator[t][r] = model.intVar("H_" + t + "_" + r, 0, 1);
                // Pour chaque journée, on parcourt les matchs et on relie l'indicateur :
                // Si l'équipe t est à domicile dans la journée r, alors H[t][r] = 1.
                // On utilise une contrainte "element" qui va chercher t dans le tableau home[r].
                IntVar[] homeMatches = new IntVar[matchesPerRound];
                for (int m = 0; m < matchesPerRound; m++) {
                    homeMatches[m] = home[r][m];
                }
                // On impose que homeIndicator vaut 1 si t est présent dans homeMatches.
                // Pour simplifier, on utilise une contrainte de reification :
                // On va créer une variable booléenne temporaire qui sera 1 si t est trouvé dans homeMatches.
                // Ici, on modélise cela par une contrainte d'égalité : on compte le nombre d'occurrences de t dans homeMatches.
                // Une approche simple est d'utiliser une contrainte globale "count".
                model.count(t, homeMatches, homeIndicator[t][r]).post();
            }
        }
        // Pour chaque équipe, limiter les matchs consécutifs à domicile.
        for (int t = 0; t < n; t++) {
            for (int r = 0; r <= rounds - (maxConsecutive + 1); r++) {
                IntVar[] window = new IntVar[maxConsecutive + 1];
                for (int k = 0; k < maxConsecutive + 1; k++) {
                    window[k] = homeIndicator[t][r + k];
                }
                model.sum(window, "<=", maxConsecutive).post();
            }
        }

        // Stratégie de recherche : ici, on utilise une stratégie simple d'inputOrder avec LB
        Solver solver = model.getSolver();
        solver.setSearch(Search.inputOrderLBSearch(model.retrieveIntVars(true)));

        // Recherche et affichage des solutions
        int nbSolutions = 3;
        while (solver.solve() && nbSolutions > 0) {
            System.out.println("=== Solution trouvée ===");
            for (int r = 0; r < rounds; r++) {
                System.out.println("Journée " + (r + 1) + " :");
                for (int m = 0; m < matchesPerRound; m++) {
                    System.out.println("  Match : Équipe " + home[r][m].getValue()
                            + " (domicile) vs Équipe " + away[r][m].getValue() + " (extérieur)");
                }
            }
            System.out.println("------------------------");
            nbSolutions--;
        }

        if (solver.getSolutionCount() == 0) {
            System.out.println("Aucune solution trouvée.");
        }
    }
}
