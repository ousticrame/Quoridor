package org.example;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;

public class RoundRobinScheduler {

    static int nbResult = 1;

    public static void run() {
        // Paramètres du tournoi
        int n = 6;  // nombre d'équipes (nombre pair)
        int rounds = n - 1; // nombre de journées
        int matchesPerRound = n / 2; // nombre de matchs par journée

        // Contrainte sur la séquence domicile/extérieur (exemple : pas plus de 2 matchs consécutifs)
        int maxConsecutive = 2;

        // Exemple de disponibilités de stades :
        // dispo[t][r] vaut true si l'équipe t peut jouer à domicile en journée r, false sinon.
        boolean[][] dispo = new boolean[n][rounds];
        // Initialisation des disponibilités (exemple arbitraire)
        // On suppose que par défaut toutes les équipes sont disponibles, sauf quelques exceptions.
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                dispo[t][r] = true;
            }
        }
        // Par exemple, l'équipe 0 n'est pas disponible à domicile lors de la journée 2 et 4.
        dispo[0][1] = false;
        dispo[0][3] = false;

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

        // Contrainte 4 : Disponibilités de stades.
        // Si l'équipe t n'est pas disponible en journée r, alors elle ne peut pas jouer à domicile (son indicateur doit être 0).
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                if (!dispo[t][r]) {
                    model.arithm(homeIndicator[t][r], "=", 0).post();
                }
            }
        }

        // Stratégie de recherche : ici, on utilise une stratégie simple d'inputOrder avec LB
        Solver solver = model.getSolver();
        solver.setSearch(Search.inputOrderLBSearch(model.retrieveIntVars(true)));

        // Recherche et affichage des solutions
        int nbSolutions = nbResult;
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
    public static void runWithRest() {
        // Paramètres du tournoi
        int n = 6;                 // nombre d'équipes (nombre pair)
        int rounds = n - 1;        // nombre de rounds (journées de championnat)
        int matchesPerRound = n / 2; // matchs par round

        // Paramètre de repos minimum (en jours) entre deux matchs successifs pour une équipe.
        int minRest = 1; // par exemple, 1 jour de repos minimum

        // Domaine du calendrier (jours de l'année par exemple)
        int D = 50; // borne supérieure du jour calendaire

        // Exemple de disponibilité de stades (pour chaque équipe et pour chaque jour du calendrier)
        // available[t][d] vaut true si l'équipe t peut jouer à domicile le jour d (d variant de 1 à D)
        boolean[][] available = new boolean[n][D+1]; // d de 1 à D (on ignore l'index 0)
        for (int t = 0; t < n; t++) {
            for (int d = 1; d <= D; d++) {
                available[t][d] = true; // par défaut, disponible
            }
        }
        // Par exemple, on peut fixer quelques indisponibilités :
        // L'équipe 0 ne peut pas jouer à domicile le jour 10 et le jour 20.
        available[0][10] = false;
        available[0][20] = false;

        // Création du modèle
        Model model = new Model("Calendrier sportif avec répartition fine");

        // Variables de match :
        // home[r][m] et away[r][m] représentent respectivement l'équipe à domicile et à l'extérieur du match m du round r.
        IntVar[][] home = new IntVar[rounds][matchesPerRound];
        IntVar[][] away = new IntVar[rounds][matchesPerRound];
        // Variable pour encoder la paire (pour garantir qu'une confrontation ne se répète qu'une fois)
        IntVar[][] pair = new IntVar[rounds][matchesPerRound];
        // Variable indiquant le jour réel (calendaire) où se joue le match
        IntVar[][] matchDay = new IntVar[rounds][matchesPerRound];

        // Création des variables pour chaque match
        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                home[r][m] = model.intVar("home_" + r + "_" + m, 0, n - 1);
                away[r][m] = model.intVar("away_" + r + "_" + m, 0, n - 1);
                model.arithm(home[r][m], "!=", away[r][m]).post();
                pair[r][m] = model.intVar("pair_" + r + "_" + m, 0, n * n - 1);
                // Chaque match se joue un jour entre 1 et D
                matchDay[r][m] = model.intVar("matchDay_" + r + "_" + m, 1, D);
            }
        }

        // Contrainte 1 : Chaque équipe joue une fois par round.
        for (int r = 0; r < rounds; r++) {
            IntVar[] teamsRound = new IntVar[n];
            int idx = 0;
            for (int m = 0; m < matchesPerRound; m++) {
                teamsRound[idx++] = home[r][m];
                teamsRound[idx++] = away[r][m];
            }
            model.allDifferent(teamsRound).post();
        }

        // Contrainte 2 : Chaque paire d'équipes se rencontre une seule fois (indépendamment de l'ordre domicile/extérieur).
        IntVar[] allPairs = new IntVar[rounds * matchesPerRound];
        int index = 0;
        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                // Variables auxiliaires pour obtenir le minimum et le maximum des équipes.
                IntVar minTeam = model.intVar("min_" + r + "_" + m, 0, n - 1);
                IntVar maxTeam = model.intVar("max_" + r + "_" + m, 0, n - 1);
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
                // Encodage unique : pair = minTeam * n + maxTeam
                model.scalar(new IntVar[]{minTeam, maxTeam}, new int[]{n, 1}, "=", pair[r][m]).post();
                allPairs[index++] = pair[r][m];
            }
        }
        model.allDifferent(allPairs).post();

        // Contrainte 3 : Disponibilité des stades.
        // Pour chaque match, le couple (équipe à domicile, matchDay) doit être dans la table des couples autorisés.
        // Construction de la table des tuples autorisés.
        Tuples allowedTuples = new Tuples(true);
        for (int t = 0; t < n; t++) {
            for (int d = 1; d <= D; d++) {
                if (available[t][d]) {
                    allowedTuples.add(t, d);
                }
            }
        }
        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                // On impose que si l'équipe jouant à domicile n'est pas disponible le jour choisi,
                // alors la solution est rejetée.
                model.table(new IntVar[]{home[r][m], matchDay[r][m]}, allowedTuples, "CT+").post();
            }
        }

        // Contrainte 4 : Repos minimum pour chaque équipe entre deux matchs consécutifs.
        // Pour chaque équipe t et pour chaque paire de rounds consécutifs,
        // si l'équipe t joue dans un match du round r et dans un match du round r+1,
        // alors la différence entre les jours de ces matchs doit être >= minRest + 1.
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds - 1; r++) {
                for (int m1 = 0; m1 < matchesPerRound; m1++) {
                    for (int m2 = 0; m2 < matchesPerRound; m2++) {
                        // Contrainte :
                        // si (t apparaît dans le match (r, m1)) ET (t apparaît dans le match (r+1, m2))
                        // alors matchDay[r+1][m2] - matchDay[r][m1] >= minRest + 1.
                        model.ifThen(
                                model.and(
                                        model.or(
                                                model.arithm(home[r][m1], "=", t),
                                                model.arithm(away[r][m1], "=", t)
                                        ),
                                        model.or(
                                                model.arithm(home[r+1][m2], "=", t),
                                                model.arithm(away[r+1][m2], "=", t)
                                        )
                                ),
                                model.arithm(matchDay[r+1][m2], "-", matchDay[r][m1], ">=", minRest + 1)
                        );
                    }
                }
            }
        }

        // Stratégie de recherche (on peut affiner selon les besoins)
        Solver solver = model.getSolver();
        solver.setSearch(Search.inputOrderLBSearch(model.retrieveIntVars(true)));

        // Recherche et affichage des solutions
        int nbSolutions = nbResult;
        while (solver.solve() && nbSolutions > 0) {
            System.out.println("=== Solution trouvée ===");
            for (int r = 0; r < rounds; r++) {
                System.out.println("Round " + (r + 1) + " :");
                for (int m = 0; m < matchesPerRound; m++) {
                    System.out.println("  Match : Équipe " + home[r][m].getValue() + " (domicile) vs Équipe "
                            + away[r][m].getValue() + " (extérieur) - Jour calendaire : " + matchDay[r][m].getValue());
                }
            }
            System.out.println("------------------------");
            nbSolutions--;
        }

        if (solver.getSolutionCount() == 0) {
            System.out.println("Aucune solution trouvée.");
        }
    }
    public static void optiRun() {
        // Paramètres du tournoi
        int n = 8;  // nombre d'équipes (nombre pair)
        int rounds = n - 1; // nombre de journées
        int matchesPerRound = n / 2; // nombre de matchs par journée

        // Contrainte sur la séquence domicile/extérieur (exemple : pas plus de 2 matchs consécutifs)
        int maxConsecutive = 2;

        // Exemple de disponibilités de stades :
        // dispo[t][r] vaut true si l'équipe t peut jouer à domicile en journée r, false sinon.
        boolean[][] dispo = new boolean[n][rounds];
        // Initialisation des disponibilités (exemple arbitraire)
        // On suppose que par défaut toutes les équipes sont disponibles, sauf quelques exceptions.
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                dispo[t][r] = true;
            }
        }
        // Par exemple, l'équipe 0 n'est pas disponible à domicile lors de la journée 2 et 4.
        // dispo[0][1] = false;
        // dispo[0][3] = false;

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

        // Contrainte 4 : Disponibilités de stades.
        // Si l'équipe t n'est pas disponible en journée r, alors elle ne peut pas jouer à domicile (son indicateur doit être 0).
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                if (!dispo[t][r]) {
                    model.arithm(homeIndicator[t][r], "=", 0).post();
                }
            }
        }

        // Pour chaque équipe t et pour chaque round r (0 ≤ r < rounds-1),
        // breakVars[t][r] vaut 1 si l'équipe t a un break entre le round r et r+1, 0 sinon.
        IntVar[][] breakVars = new IntVar[n][rounds - 1];
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds - 1; r++) {
                breakVars[t][r] = model.intVar("break_" + t + "_" + r, 0, 1);
                // Ici, vous devez ajouter les contraintes liant breakVars[t][r] à vos variables "place"
                // ou à vos indicateurs de domicile/extérieur pour déterminer s'il y a break ou non.
                // Par exemple :
                model.ifThenElse(
                    model.arithm(homeIndicator[t][r], "=", homeIndicator[t][r+1]),
                    model.arithm(breakVars[t][r], "=", 1),
                    model.arithm(breakVars[t][r], "=", 0)
                );
            }
        }

        // Supposons que pour chaque équipe t, breakCount[t] est une variable qui compte le nombre de breaks de t.
        IntVar[] breakCount = new IntVar[n];
        for (int t = 0; t < n; t++) {
            // Domaine possible : de 0 à (rounds-1) par exemple
            breakCount[t] = model.intVar("breakCount_" + t, 0, rounds - 1);
            // Lier breakCount[t] aux variables break associées à l'équipe t
            // Ici, breakVars[t] est le tableau des breaks pour l'équipe t (de 0 à rounds-2)
            model.sum(breakVars[t], "=", breakCount[t]).post();
        }

        IntVar totalBreaks = model.intVar("totalBreaks", 0, n * (rounds - 1));
        model.sum(breakCount, "=", totalBreaks).post();
        model.arithm(totalBreaks, "=", n - 2).post(); // La solution est valide uniquement si totalBreaks == n-2

        // Stratégie de recherche : ici, on utilise une stratégie simple d'inputOrder avec LB
        Solver solver = model.getSolver();
        // solver.showStatistics();
        // solver.showSolutions();
        solver.setSearch(Search.inputOrderLBSearch(model.retrieveIntVars(true)));

        // Recherche et affichage des solutions
        int nbSolutions = nbResult;
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
