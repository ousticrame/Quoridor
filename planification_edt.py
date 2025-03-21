from ortools.sat.python import cp_model

###########################
### DONNÉES DU PROBLÈME ###
###########################

cours_par_semaines = {
    "Histoire": 4,
    "Maths": 6,
    "Physique-Chimie": 6,
    "Philosophie": 4,
    "Sport": 3,
    "Anglais": 3,
    "Espagnol": 2,
    "Maths expertes": 2
}

# Créneaux horaires disponibles
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
heures = ["8h30-9h30", "9h30-10h30", "10h30-11h30", "11h30-12h30",
          "14h-15h", "15h-16h", "16h-17h", "17h-18h"]

# Nombre de classes et salles
nb_classes = 3
nb_salles = 3

########################
### MODÉLISATION CSP ###
########################

# Modèle CSP
model = cp_model.CpModel()

# VARIABLES
# x[cours, jour, heure, classe, salle] = 1 si le cours est programmé à ce créneau, sinon 0
x = {}
for cours_nom in cours_par_semaines:
    for jour in jours:
        for heure in heures:
            for classe in range(nb_classes):
                for salle in range(nb_salles):
                    x[(cours_nom, jour, heure, classe, salle)] = model.NewBoolVar(
                        f'{cours_nom}_{jour}_{heure}_classe{classe}_salle{salle}')

# CONTRAINTES
# 1. Chaque classe doit avoir le nombre d'heures requis par semaine pour chaque cours
for cours_nom, nb_heures in cours_par_semaines.items():
    for classe in range(nb_classes):
        model.Add(sum(x[(cours_nom, jour, heure, classe, salle)]
                      for jour in jours
                      for heure in heures
                      for salle in range(nb_salles)) == nb_heures)

# 2. Pas plus de deux heures d'un même cours à la suite pour une classe
for cours_nom in cours_par_semaines:
    for jour in jours:
        for i in range(len(heures) - 1):
            for classe in range(nb_classes):
                model.Add(sum(x[(cours_nom, jour, heures[i], classe, salle)] for salle in range(nb_salles)) +
                          sum(x[(cours_nom, jour, heures[i + 1], classe, salle)] for salle in range(nb_salles)) <= 1)

# 3. Une classe ne peut pas avoir deux cours en même temps
for jour in jours:
    for heure in heures:
        for classe in range(nb_classes):
            model.Add(sum(x[(cours_nom, jour, heure, classe, salle)]
                          for cours_nom in cours_par_semaines
                          for salle in range(nb_salles)) <= 1)

# 4. Une salle ne peut pas être utilisée par deux cours en même temps
for jour in jours:
    for heure in heures:
        for salle in range(nb_salles):
            model.Add(sum(x[(cours_nom, jour, heure, classe, salle)]
                          for cours_nom in cours_par_semaines
                          for classe in range(nb_classes)) <= 1)

# 5. Un même cours ne peut pas être enseigné dans deux classes différentes au même moment
# (pour représenter la disponibilité des enseignants)
for cours_nom in cours_par_semaines:
    for jour in jours:
        for heure in heures:
            model.Add(sum(x[(cours_nom, jour, heure, classe, salle)]
                          for classe in range(nb_classes)
                          for salle in range(nb_salles)) <= 1)

# Résolution
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Affichage des résultats
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution trouvée :")

    # Affichage par classe
    for classe in range(nb_classes):
        print(f"\n===== EMPLOI DU TEMPS CLASSE {classe} =====")

        # Créer une matrice d'emploi du temps vide
        edt = {}
        for jour in jours:
            edt[jour] = {}
            for heure in heures:
                edt[jour][heure] = "---"

        # Remplir la matrice
        for cours_nom in cours_par_semaines:
            for jour in jours:
                for heure in heures:
                    for salle in range(nb_salles):
                        if solver.BooleanValue(x[(cours_nom, jour, heure, classe, salle)]):
                            edt[jour][heure] = f"{cours_nom} (Salle {salle})"

        # Afficher la matrice
        print(f"{'Horaire':12}", end="")
        for jour in jours:
            print(f"{jour:28}", end="")
        print()

        for heure in heures:
            print(f"{heure:12}", end="")
            for jour in jours:
                print(f"{edt[jour][heure]:28}", end="")
            print()

        # Vérification du nombre d'heures par matière
        print("\nRécapitulatif des heures par matière:")
        for cours_nom, nb_heures in cours_par_semaines.items():
            heures_planifiees = sum(1 for jour in jours for heure in heures for salle in range(nb_salles)
                                    if solver.BooleanValue(x[(cours_nom, jour, heure, classe, salle)]))
            print(f"{cours_nom}: {heures_planifiees}/{nb_heures} heures")
else:
    print("Aucune solution trouvée.")