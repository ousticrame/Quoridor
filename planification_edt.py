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
for cours in cours_par_semaines:
    for jour in jours:
        for heure in heures:
            for classe in range(nb_classes):
                for salle in range(nb_salles):
                    x[(cours, jour, heure, classe, salle)] = model.NewBoolVar(f'{cours}_{jour}_{heure}_classe{classe}_salle{salle}')
print(x)

# CONTRAINTES
# 1. Chaque cours doit avoir le nombre d'heures requis par semaine
for cours, nb_heures in cours_par_semaines.items():
    model.Add(sum(x[(cours, jour, heure, classe, salle)]
                   for jour in jours
                   for heure in heures
                   for classe in range(nb_classes)
                   for salle in range(nb_salles)) == nb_heures)

# 2. Pas plus de deux heures d'un même cours à la suite
for cours in cours_par_semaines:
    for jour in jours:
        for i in range(len(heures) - 1):
            for classe in range(nb_classes):
                for salle in range(nb_salles):
                    model.Add(x[(cours, jour, heures[i], classe, salle)] +
                              x[(cours, jour, heures[i + 1], classe, salle)] <= 1)

# 3. Un professeur ne peut pas donner deux cours en même temps
for jour in jours:
    for heure in heures:
        for classe in range(nb_classes):
            for salle in range(nb_salles):
                model.Add(sum(x[(cours, jour, heure, classe, salle)] for cours in cours_par_semaines) <= 1)

# 4. Une salle ne peut pas être utilisée par deux cours en même temps
for jour in jours:
    for heure in heures:
        for salle in range(nb_salles):
            model.Add(sum(x[(cours, jour, heure, classe, salle)]
                           for cours in cours_par_semaines
                           for classe in range(nb_classes)) <= 1)

# Résolution
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Affichage des résultats
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution trouvée :")
    for cours in cours_par_semaines:
        print(f"\n{cours}:")
        for jour in jours:
            for heure in heures:
                for classe in range(nb_classes):
                    for salle in range(nb_salles):
                        if solver.BooleanValue(x[(cours, jour, heure, classe, salle)]):
                            print(f"  {jour} {heure} - Classe {classe} - Salle {salle}")
else:
    print("Aucune solution trouvée.")
