from ortools.sat.python import cp_model

def create_university_timetabling():
    """
    Exemple de planification d'emplois du temps pour 3 classes de terminale,
    8 professeurs, 4 salles, sur 5 jours (Lundi-Vendredi), avec des créneaux
    d'une heure chacun entre 8h30-12h30 et 14h-18h (8 créneaux par jour).

    Objectif :
      - Minimiser les 'trous' (gap) dans l’emploi du temps
      - Éviter (autant que possible) les cours après 17h
    """

    # -------------------------------
    # Paramètres GÉNÉRAUX du problème
    # -------------------------------

    # Jours de la semaine (lundi=0 ... vendredi=4)
    num_days = 5

    # On découpe la journée en 8 créneaux d'1h : 8h30-9h30, 9h30-10h30,
    # 10h30-11h30, 11h30-12h30, 14h00-15h00, 15h00-16h00, 16h00-17h00, 17h00-18h00
    slots_per_day = 8

    # Nombre de salles disponibles en parallèle
    num_rooms = 4

    # On suppose qu'on a 3 classes : T1, T2, T3
    classes = ["T1", "T2", "T3"]

    # 8 professeurs (un par matière dans cet exemple simple)
    teachers = {
        "MATHS":    "Prof_Math",
        "PHYSICS":  "Prof_Phys",
        "CHEM":     "Prof_Chem",
        "ENGLISH":  "Prof_Eng",
        "HISTORY":  "Prof_Hist",
        "GEO":      "Prof_Geo",
        "FRENCH":   "Prof_Fr",
        "PE":       "Prof_PE",
    }

    # Nombre d'heures par semaine exigé pour chaque matière et pour CHAQUE classe
    subject_hours = {
        "MATHS":   4,
        "PHYSICS": 3,
        "CHEM":    2,
        "ENGLISH": 3,
        "HISTORY": 3,
        "GEO":     2,
        "FRENCH":  3,
        "PE":      2
    }

    subjects = list(subject_hours.keys())

    # -------------------------------
    # Création du solveur
    # -------------------------------
    model = cp_model.CpModel()

    # --------------------------------------------------
    # Variable X[c, s, d, h] = 1 si la classe c a le cours s
    #                          (matière s) au jour d, créneau h
    # --------------------------------------------------
    X = {}
    for c_idx, c in enumerate(classes):
        for s_idx, s in enumerate(subjects):
            for d in range(num_days):
                for h in range(slots_per_day):
                    X[(c_idx, s_idx, d, h)] = model.NewBoolVar(
                        f"X_class{c}_subj{s}_day{d}_slot{h}"
                    )

    # --------------------------------------------------
    # 1) Respect du nombre d'heures exigé par matière et par classe
    # --------------------------------------------------
    for c_idx, c in enumerate(classes):
        for s_idx, s in enumerate(subjects):
            required = subject_hours[s]
            model.Add(
                sum(X[(c_idx, s_idx, d, h)]
                    for d in range(num_days)
                    for h in range(slots_per_day)) == required
            )

    # --------------------------------------------------
    # 2) Pour une même classe, impossible d'avoir 2 matières
    #    simultanément sur un même créneau
    #    => sum_s X[(c, s, d, h)] <= 1
    # --------------------------------------------------
    for c_idx in range(len(classes)):
        for d in range(num_days):
            for h in range(slots_per_day):
                model.Add(
                    sum(X[(c_idx, s_idx, d, h)] for s_idx in range(len(subjects))) <= 1
                )

    # --------------------------------------------------
    # 3) Le même professeur ne peut pas enseigner à deux classes
    #    en même temps.
    #    Puisque dans cet exemple un prof = 1 matière,
    #    => On interdit qu'une même matière s'apparaisse
    #    sur deux classes simultanément.
    #
    #    Autrement dit, pour chaque s, d, h:
    #    sum_c X[(c, s, d, h)] <= 1
    # --------------------------------------------------
    for s_idx, s in enumerate(subjects):
        for d in range(num_days):
            for h in range(slots_per_day):
                model.Add(
                    sum(X[(c_idx, s_idx, d, h)] for c_idx in range(len(classes))) <= 1
                )

    # --------------------------------------------------
    # 4) Capacité salles : max "num_rooms" cours en même temps
    #    (peu importe la matière ni la classe).
    # --------------------------------------------------
    for d in range(num_days):
        for h in range(slots_per_day):
            model.Add(
                sum(X[(c_idx, s_idx, d, h)]
                    for c_idx in range(len(classes))
                    for s_idx in range(len(subjects))) <= num_rooms
            )

    # --------------------------------------------------
    # 5) Un cours ne doit pas excéder 2 heures consécutives
    #    => pour chaque (c, s, d), pour h dans [0..slots_per_day-3],
    #       X[c,s,d,h] + X[c,s,d,h+1] + X[c,s,d,h+2] <= 2
    # --------------------------------------------------
    for c_idx in range(len(classes)):
        for s_idx in range(len(subjects)):
            for d in range(num_days):
                for h in range(slots_per_day - 2):
                    model.Add(
                        X[(c_idx, s_idx, d, h)] +
                        X[(c_idx, s_idx, d, h+1)] +
                        X[(c_idx, s_idx, d, h+2)] <= 2
                    )

    # --------------------------------------------------
    # 6) Minimiser les "trous" (gap) pour les élèves
    #
    #    On introduit d'abord Y[c,d,h] = 1 si la classe c a un cours
    #    (n'importe quelle matière) au jour d, slot h.
    #
    #    Puis un trou (gap) = pattern "cours - pas cours - cours"
    # --------------------------------------------------
    Y = {}
    for c_idx in range(len(classes)):
        for d in range(num_days):
            for h in range(slots_per_day):
                Y[(c_idx, d, h)] = model.NewBoolVar(f"Y_class{c_idx}_day{d}_slot{h}")
                # Y = 1 <=> sum_s X[c,s,d,h] = 1
                model.Add(Y[(c_idx, d, h)] ==
                          sum(X[(c_idx, s_idx, d, h)] for s_idx in range(len(subjects))))

    gaps = []
    for c_idx in range(len(classes)):
        for d in range(num_days):
            for h in range(slots_per_day - 2):
                gap_var = model.NewBoolVar(f"gap_c{c_idx}_d{d}_h{h}")
                # gap_var = 1 si Y(c,d,h)=1 ET Y(c,d,h+1)=0 ET Y(c,d,h+2)=1
                model.Add(gap_var <= Y[(c_idx, d, h)])
                model.Add(gap_var <= 1 - Y[(c_idx, d, h+1)])
                model.Add(gap_var <= Y[(c_idx, d, h+2)])
                # Pour être sûr que gap_var=1 => ces trois conditions sont satisfaites
                # on ajoute la contrainte inverse par addition :
                # gap_var >= Y[(c_idx, d, h)] + (1 - Y[(c_idx, d, h+1)]) + Y[(c_idx, d, h+2]) - 2
                model.Add(gap_var >= Y[(c_idx, d, h)]
                                      + (1 - Y[(c_idx, d, h+1)])
                                      + Y[(c_idx, d, h+2)] - 2)
                gaps.append(gap_var)

    # --------------------------------------------------
    # 7) Pénaliser les cours après 17h = slot 7
    #    => On met un petit coût pour chaque cours planifié en slot 7
    # --------------------------------------------------
    late_vars = []
    last_slot = 7  # 17h00-18h00
    for c_idx in range(len(classes)):
        for s_idx in range(len(subjects)):
            for d in range(num_days):
                lv = model.NewBoolVar(f"late_c{c_idx}_s{s_idx}_d{d}")
                model.Add(lv == X[(c_idx, s_idx, d, last_slot)])
                late_vars.append(lv)

    # --------------------------------------------------
    # 8) Fonction Objectif
    #    - Priorité : réduire le nombre de trous (chaque trou = 10)
    #    - Second : éviter les cours après 17h (coût = 1)
    # --------------------------------------------------
    model.Minimize(10 * sum(gaps) + sum(late_vars))

    # ------------------
    # Lancement du solver
    # ------------------
    solver = cp_model.CpSolver()
    solver.MaxTimeInSeconds = 30.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("\n=== SOLUTION TROUVÉE ===")
        print(f"Coût objectif = {solver.ObjectiveValue()} (plus petit = mieux)")

        # Affichons l'emploi du temps de chaque classe
        day_header = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        slot_strs = [
            "08h30-09h30", "09h30-10h30", "10h30-11h30", "11h30-12h30",
            "14h00-15h00", "15h00-16h00", "16h00-17h00", "17h00-18h00"
        ]

        for c_idx, c in enumerate(classes):
            print(f"\nEmploi du temps de la classe {c}:")
            for d in range(num_days):
                print(f"  {day_header[d]} :")
                for h in range(slots_per_day):
                    # Cherchons s'il y a un cours planifié
                    for s_idx, s in enumerate(subjects):
                        if solver.Value(X[(c_idx, s_idx, d, h)]) == 1:
                            print(f"    {slot_strs[h]} -> {s}")
    else:
        print("Aucune solution réalisable trouvée (ou résolution incomplète).")


if __name__ == "__main__":
    create_university_timetabling()