#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ortools.sat.python import cp_model


def get_time(slot):
    """
    Renvoie l'heure de début correspondant à un slot (0 à 7).
    Matin : 0 → 8h30, 1 → 9h30, 2 → 10h30, 3 → 11h30.
    Après-midi : 4 → 14h00, 5 → 15h00, 6 → 16h00, 7 → 17h00.
    """
    mapping = {
        0: "8h30",
        1: "9h30",
        2: "10h30",
        3: "11h30",
        4: "14h00",
        5: "15h00",
        6: "16h00",
        7: "17h00"
    }
    return mapping.get(slot, f"Slot {slot}")


def main():
    # ------------------------------
    # 1. Définition des données du problème
    # ------------------------------
    classes = ["Terminale A", "Terminale B", "Terminale C"]
    subjects = ["Maths", "Physique-Chimie", "SVT", "Histoire-Géo",
                "Anglais", "Espagnol", "Philosophie", "EPS"]
    # Chaque matière correspond à un enseignant unique.
    rooms = ["Salle 101", "Salle 102", "Salle 201", "Salle 202"]
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    slots_per_day = list(range(8))  # Slots 0 à 7 par jour
    num_days = len(days)
    num_slots = len(slots_per_day)
    total_slots = num_days * num_slots  # 5 * 8 = 40

    # Volume horaire requis par classe et matière (en heures par semaine)
    hours_per_week = {
        "Terminale A": {"Maths": 4, "Physique-Chimie": 4, "SVT": 2, "Histoire-Géo": 3,
                        "Anglais": 2, "Espagnol": 2, "Philosophie": 4, "EPS": 2},
        "Terminale B": {"Maths": 4, "Physique-Chimie": 4, "SVT": 2, "Histoire-Géo": 3,
                        "Anglais": 2, "Espagnol": 2, "Philosophie": 4, "EPS": 2},
        "Terminale C": {"Maths": 4, "Physique-Chimie": 4, "SVT": 2, "Histoire-Géo": 3,
                        "Anglais": 2, "Espagnol": 2, "Philosophie": 4, "EPS": 2}
    }

    # ------------------------------
    # 2. Création du modèle et des variables
    # ------------------------------
    model = cp_model.CpModel()

    # Variables de décision : X[(c, s, t, r)] = 1 si la classe c a un cours de s au créneau t dans la salle r.
    X = {}
    for c in classes:
        for s in subjects:
            for d in range(num_days):
                for h in slots_per_day:
                    t = d * num_slots + h
                    for r in rooms:
                        var_name = f"x_{c}_{s}_{d}_{h}_{r}"
                        X[c, s, t, r] = model.NewBoolVar(var_name)

    # ------------------------------
    # 3. Ajout des contraintes
    # ------------------------------

    # (a) Une classe ne peut avoir qu'un seul cours par créneau
    for c in classes:
        for t in range(total_slots):
            model.Add(sum(X[c, s, t, r] for s in subjects for r in rooms) <= 1)

    # (b) Un enseignant (associé à une matière) ne peut enseigner qu'à une seule classe à un créneau
    for s in subjects:
        for t in range(total_slots):
            model.Add(sum(X[c, s, t, r] for c in classes for r in rooms) <= 1)

    # (c) Une salle ne peut accueillir plus d'un cours par créneau
    for r in rooms:
        for t in range(total_slots):
            model.Add(sum(X[c, s, t, r] for c in classes for s in subjects) <= 1)

    # (d) Chaque classe doit recevoir le volume horaire exact pour chaque matière
    for c in classes:
        for s in subjects:
            total_hours = hours_per_week[c][s]
            model.Add(sum(X[c, s, t, r] for t in range(total_slots) for r in rooms) == total_hours)

    # (e) Pas plus de 2h consécutives pour un même cours (pour éviter des cours de plus de 2h)
    for c in classes:
        for s in subjects:
            for d in range(num_days):
                # Matin : slots 0 à 3 (créneaux relatifs)
                for h in range(0, 2):  # fenêtres : [0,1,2] et [1,2,3]
                    t0 = d * num_slots + h
                    t1 = d * num_slots + h + 1
                    t2 = d * num_slots + h + 2
                    model.Add(sum(X[c, s, time, r] for r in rooms for time in [t0, t1, t2]) <= 2)
                # Après-midi : slots 4 à 7
                for h in range(4, 6):  # fenêtres : [4,5,6] et [5,6,7]
                    t0 = d * num_slots + h
                    t1 = d * num_slots + h + 1
                    t2 = d * num_slots + h + 2
                    model.Add(sum(X[c, s, time, r] for r in rooms for time in [t0, t1, t2]) <= 2)

    # ------------------------------
    # 4. Préférences dans la fonction objectif
    # ------------------------------

    # Minimiser les cours tardifs et les créneaux vides (gaps)
    # Définir les créneaux de fin de journée (par exemple, slot 7 correspond à 17h00)
    late_slots = [d * num_slots + 7 for d in range(num_days)]

    # Variables pour détecter les "trous" dans la journée (gap : créneau vide suivi d'un cours)
    G = {}
    for c in classes:
        for d in range(num_days):
            # Matin : slots 0 à 2
            for h in range(0, 3):
                t_current = d * num_slots + h
                t_next = d * num_slots + h + 1
                G[c, d, h] = model.NewBoolVar(f"gap_{c}_{d}_{h}")
                model.Add(sum(X[c, s, t_current, r] for s in subjects for r in rooms) == 0).OnlyEnforceIf(G[c, d, h])
                model.Add(sum(X[c, s, t_next, r] for s in subjects for r in rooms) >= 1).OnlyEnforceIf(G[c, d, h])
            # Après-midi : slots 4 à 6
            for h in range(4, 7):
                t_current = d * num_slots + h
                t_next = d * num_slots + h + 1
                G[c, d, h] = model.NewBoolVar(f"gap_{c}_{d}_{h}")
                model.Add(sum(X[c, s, t_current, r] for s in subjects for r in rooms) == 0).OnlyEnforceIf(G[c, d, h])
                model.Add(sum(X[c, s, t_next, r] for s in subjects for r in rooms) >= 1).OnlyEnforceIf(G[c, d, h])

    objective_terms = []
    # Pénaliser les cours tardifs (créneaux 7 de chaque jour)
    for t in late_slots:
        for c in classes:
            for s in subjects:
                for r in rooms:
                    objective_terms.append(X[c, s, t, r])
    # Pénaliser les gaps
    for gap_var in G.values():
        objective_terms.append(gap_var)
    model.Minimize(sum(objective_terms))

    # ------------------------------
    # 5. Résolution du modèle
    # ------------------------------
    solver = cp_model.CpSolver()
    result_status = solver.Solve(model)

    # ------------------------------
    # 6. Affichage des résultats
    # ------------------------------
    if result_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # Construire une structure de planning : par classe, par jour, par slot
        schedule = {c: {day: {} for day in days} for c in classes}
        for c in classes:
            for d in range(num_days):
                for h in slots_per_day:
                    t = d * num_slots + h
                    for s in subjects:
                        for r in rooms:
                            if solver.Value(X[c, s, t, r]) == 1:
                                # On s'assure qu'il n'y a qu'un cours par créneau pour la classe
                                if h in schedule[c][days[d]]:
                                    schedule[c][days[d]][h] += f" / {s} en {r}"
                                else:
                                    schedule[c][days[d]][h] = f"{s} en {r}"

        # Affichage formaté : pour chaque classe, afficher les jours triés avec les horaires
        for c in classes:
            print(f"\nEmploi du temps de {c} :")
            for d in days:
                print(f"  {d} :")
                if schedule[c][d]:
                    for h in sorted(schedule[c][d].keys()):
                        print(f"    {get_time(h)} : {schedule[c][d][h]}")
                else:
                    print("    Pas de cours")
    else:
        print("Aucune solution n'a pu être trouvée avec les contraintes données.")


if __name__ == "__main__":
    main()