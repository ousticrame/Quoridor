from nbclient.cli import nbclient_flags, nbclient_aliases
from ortools.sat.python import cp_model

###########################
### DONNÉES DU PROBLÈME ###
###########################

matieres = {
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

jours_str = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
nb_jours = len(jours_str)

heures_str = ["8h30-9h30", "9h30-10h30", "10h30-11h30", "11h30-12h30",
          "14h-15h", "15h-16h", "16h-17h", "17h-18h"]
nb_heures = len(heures_str)

# Nombre de classes et salles
nb_classes = 3
nb_salles = 3

########################
### MODÉLISATION CSP ###
########################

# Modèle CSP
model = cp_model.CpModel()


#################
### VARIABLES ###
#################

# x[cours, jour, heure, classe, salle] = 1 si le cours est programmé à ce créneau, sinon 0
x = {}
for nom_matiere in matieres:
    for jour in range(nb_jours):
        for heure in range(nb_heures):
            for classe in range(nb_classes):
                for salle in range(nb_salles):
                    x[(nom_matiere, jour, heure, classe, salle)] = model.NewBoolVar(
                        f'{nom_matiere}_{jour}_{heure}_classe{classe}_salle{salle}')


###################
### CONTRAINTES ###
###################

# 1. Chaque classe doit avoir le nombre d'nb_heures requis par semaine pour chaque cours
for nom_matiere, heures_matiere in matieres.items():
    for classe in range(nb_classes):
        model.Add(sum(x[(nom_matiere, jour, heure, classe, salle)]
                      for jour in range(nb_jours)
                      for heure in range(nb_heures)
                      for salle in range(nb_salles)) == heures_matiere)

# 2. Pas plus de deux nb_heures d'un même cours à la suite pour une classe
for nom_matiere in matieres:
    for jour in range(nb_jours):
        for i in range(nb_heures - 2):
            for classe in range(nb_classes):
                model.Add(
                    sum(x[(nom_matiere, jour, i, classe, salle)] for salle in range(nb_salles)) +
                    sum(x[(nom_matiere, jour, i + 1, classe, salle)] for salle in range(nb_salles)) +
                    sum(x[(nom_matiere, jour, i + 2, classe, salle)] for salle in range(nb_salles)) < 3
                )

# 3. Une classe ne peut pas avoir deux cours en même temps
for jour in range(nb_jours):
    for heure in range(nb_heures):
        for classe in range(nb_classes):
            model.Add(sum(x[(nom_matiere, jour, heure, classe, salle)]
                          for nom_matiere in matieres
                          for salle in range(nb_salles)) <= 1)

# 4. Une salle ne peut pas être utilisée par deux cours en même temps
for jour in range(nb_jours):
    for heure in range(nb_heures):
        for salle in range(nb_salles):
            model.Add(
                sum(x[(nom_matiere, jour, heure, classe, salle)]
                    for nom_matiere in matieres
                    for classe in range(nb_classes)) <= 1
            )

# 5. Un même cours ne peut pas être enseigné dans deux classes différentes au même moment
# (pour représenter la disponibilité des enseignants)
for nom_matiere in matieres:
    for jour in range(nb_jours):
        for heure in range(nb_heures):
            model.Add(sum(x[(nom_matiere, jour, heure, classe, salle)]
                          for classe in range(nb_classes)
                          for salle in range(nb_salles)) <= 1)


####################
### MINIMISATION ###
####################

# 6. Minimiser les "trous" pour les élèves

# On créé Y[c, j, h] = 1 si la classe c a un cours (de n'importe quelle matière) le jour j à l'heure h.
Y = {}
for classe in range(nb_classes):
    for jour in range(nb_jours):
        for heure in range(nb_heures):
            Y[(classe, jour, heure)] = model.NewBoolVar(f"Y_classe{classe}_{jour}_{heure}")
            # Y = 1 <=> sum_s X[c,s,d,h] = 1
            model.Add(Y[(classe, jour, heure)] ==
                sum(x[(nom_matiere, jour, heure, classe, salle)]
                    for nom_matiere in matieres
                    for salle in range(nb_salles)
                    )
                )

# On créé trou = pattern "cours - pas cours - cours"
#TODO: Implementer la détéction de trous plus grands
trous = []
for classe in range(nb_classes):
    for jour in range(nb_jours):
        # Pour les trous d'une heure
        for heure in range(nb_heures - 2):
            trou1 = model.NewBoolVar(f"trou1_classe{classe}_{jour}_{heure}")
            # trou = 1 si Y(c,d,h)=1 ET Y(c,d,h+1)=0 ET Y(c,d,h+2)=1
            model.Add(trou1 <= Y[(classe, jour, heure)])
            model.Add(trou1 <= 1 - Y[(classe, jour, heure + 1)])
            model.Add(trou1 <= Y[(classe, jour, heure + 2)])
            # Pour être sûr que trou=1 => ces trois conditions sont satisfaites
            # on ajoute la contrainte inverse par addition :
            # trou >= Y[(c_idx, d, h)] + (1 - Y[(c_idx, d, h+1)]) + Y[(c_idx, d, h+2]) - 2
            model.Add(trou1 >= Y[(classe, jour, heure)]
                      + (1 - Y[(classe, jour, heure + 1)])
                      + Y[(classe, jour, heure + 2)] - 2)
            trous.append(trou1)

        # Pour les trous de deux heures
        for heure in range(nb_heures - 3):
            trou2 = model.NewBoolVar(f"trou2_classe{classe}_{jour}_{heure}")

            model.Add(trou2 <= Y[(classe, jour, heure)])
            model.Add(trou2 <= 1 - Y[(classe, jour, heure + 1)])
            model.Add(trou2 <= 1 - Y[(classe, jour, heure + 2)])
            model.Add(trou2 <= Y[(classe, jour, heure + 3)])
            # Pour être sûr que trou=1 => ces trois conditions sont satisfaites
            # on ajoute la contrainte inverse par addition :
            # trou >= Y[(c_idx, d, h)] + (1 - Y[(c_idx, d, h+1)]) + Y[(c_idx, d, h+2]) - 2
            model.Add(trou2 >= Y[(classe, jour, heure)]
                      + (1 - Y[(classe, jour, heure + 1)])
                      + (1 - Y[(classe, jour, heure + 2)])
                      + Y[(classe, jour, heure + 3)] - 3)
            trous.append(trou2)

            # Pour les trous de trois heures
            for heure in range(nb_heures - 4):
                trou3 = model.NewBoolVar(f"trou3_classe{classe}_{jour}_{heure}")

                model.Add(trou3 <= Y[(classe, jour, heure)])
                model.Add(trou3 <= 1 - Y[(classe, jour, heure + 1)])
                model.Add(trou3 <= 1 - Y[(classe, jour, heure + 2)])
                model.Add(trou3 <= 1 - Y[(classe, jour, heure + 3)])
                model.Add(trou3 <= Y[(classe, jour, heure + 4)])
                # Pour être sûr que trou=1 => ces trois conditions sont satisfaites
                # on ajoute la contrainte inverse par addition :
                # trou >= Y[(c_idx, d, h)] + (1 - Y[(c_idx, d, h+1)]) + Y[(c_idx, d, h+2]) - 2
                model.Add(trou3 >= Y[(classe, jour, heure)]
                          + (1 - Y[(classe, jour, heure + 1)])
                          + (1 - Y[(classe, jour, heure + 2)])
                          + (1 - Y[(classe, jour, heure + 3)])
                          + Y[(classe, jour, heure + 4)] - 4)
                trous.append(trou3)

# 7. Minimiser les cours après 17h
# On met un coût pour chaque cours planifié après 17h
cours_tard = []
dernier_cours = 7  # 17h00-18h00
for classe in range(nb_classes):
    for nom_matiere in matieres:
        for jour in range(nb_jours):
            for salle in range(nb_salles):
                ct = model.NewBoolVar(f"cours_tardif_classe{classe}_{nom_matiere}_{jour}")
                model.Add(ct == x[(nom_matiere, jour, dernier_cours, classe, salle)])
                cours_tard.append(ct)

# On minimise
#    - Priorité : réduire le nombre de trous (chaque trou = 10)
#    - Second : éviter les cours après 17h (coût = 1)
model.Minimize(10 * sum(trous) + sum(cours_tard))
# Résolution
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Affichage des résultats
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution trouvée :")
    print(f"Coût objectif = {solver.ObjectiveValue()} (plus petit = mieux)")

    # Affichage par classe
    for classe in range(nb_classes):
        print(f"\n===== EMPLOI DU TEMPS CLASSE {classe} =====")

        # Créer une matrice d'emploi du temps vide
        edt = {}
        for jour in range(nb_jours):
            edt[jour] = {}
            for heure in range(nb_heures):
                edt[jour][heure] = "---"

        # Remplir la matrice
        for nom_matiere in matieres:
            for jour in range(nb_jours):
                for heure in range(nb_heures):
                    for salle in range(nb_salles):
                        if solver.BooleanValue(x[(nom_matiere, jour, heure, classe, salle)]):
                            edt[jour][heure] = f"{nom_matiere} (Salle {salle})"

        # Afficher la matrice
        print(f"{'Horaire':12}", end="")
        for jour in range(nb_jours):
            print(f"{jours_str[jour]:28}", end="")
        print()

        for heure in range(nb_heures):
            print(f"{heures_str[heure]:12}", end="")
            for jour in range(nb_jours):
                print(f"{edt[jour][heure]:28}", end="")
            print()

        # Vérification du nombre d'nb_heures par matière
        print("\nRécapitulatif des nb_heures par matière:")
        for nom_matiere, heures_matiere in matieres.items():
            heures_planifiees = sum(1 for jour in range(nb_jours) for heure in range(nb_heures) for salle in range(nb_salles)
                                    if solver.BooleanValue(x[(nom_matiere, jour, heure, classe, salle)]))
            print(f"{nom_matiere}: {heures_planifiees}/{heures_matiere} nb_heures")
else:
    print("Aucune solution trouvée.")