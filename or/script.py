from ortools.sat.python import cp_model
from datetime import datetime, timedelta

class Team:
    def __init__(self, name, stadium):
        self.name = name
        self.stadium = stadium

class Stadium:
    def __init__(self, name, unavailable_dates=None):
        self.name = name
        self.unavailable_dates = set()
        if unavailable_dates:
            for date in unavailable_dates:
                if isinstance(date, str):
                    self.unavailable_dates.add(datetime.fromisoformat(date).date())
                elif isinstance(date, datetime):
                    self.unavailable_dates.add(date.date())
                else:
                    try:
                        self.unavailable_dates.add(date)
                    except Exception:
                        pass

    def is_available_on(self, date):
        d = date.date() if isinstance(date, datetime) else date
        return d not in self.unavailable_dates

class Schedule:
    def __init__(self, teams, start_date, max_consecutive_away, max_total_breaks):
        self.teams = teams
        self.start_date = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        self.max_consecutive_away = max_consecutive_away
        self.num_teams = len(teams)
        # Pour un tournoi round-robin complet, on utilise généralement n-1 journées.
        self.num_days = self.num_teams - 1
        model = cp_model.CpModel()

        # --- Pré-calcul des jours disponibles pour chaque équipe.
        valid_days = {
            t: [d for d in range(self.num_days)
                if teams[t].stadium.is_available_on(self.start_date + timedelta(days=d))]
            for t in range(self.num_teams)
        }

        # --- Création des variables de match seulement pour les jours valides.
        self.X = {}
        for i in range(self.num_teams):
            for j in range(self.num_teams):
                if i == j:
                    continue
                for d in valid_days[i]:
                    self.X[(i, j, d)] = model.NewBoolVar(f"match_{i}_{j}_day{d+1}")

        # --- Contraintes de base.
        # 1. Chaque paire d’équipes se rencontre au plus une fois.
        for i in range(self.num_teams):
            for j in range(i + 1, self.num_teams):
                model.Add(
                    sum(self.X.get((i, j, d), 0) for d in range(self.num_days)) +
                    sum(self.X.get((j, i, d), 0) for d in range(self.num_days))
                    <= 1
                )

        # 2. Une équipe joue un match par journée.
        for t in range(self.num_teams):
            for d in range(self.num_days):
                model.Add(
                    sum(self.X.get((t, o, d), 0) for o in range(self.num_teams) if o != t) +
                    sum(self.X.get((o, t, d), 0) for o in range(self.num_teams) if o != t)
                    == 1
                )

        # # 3. Chaque équipe joue au moins un match dans le tournoi.
        # for t in range(self.num_teams):
        #     model.Add(
        #         sum(self.X.get((t, o, d), 0)
        #             for o in range(self.num_teams) if t != o
        #             for d in range(self.num_days)) +
        #         sum(self.X.get((o, t, d), 0)
        #             for o in range(self.num_teams) if t != o
        #             for d in range(self.num_days))
        #         >= 1
        #     )

        # 4. Limiter le nombre de matchs consécutifs à l’extérieur.
        for t in range(self.num_teams):
            if self.max_consecutive_away < self.num_days:
                for d0 in range(self.num_days - self.max_consecutive_away):
                    model.Add(
                        sum(self.X.get((o, t, d), 0)
                            for d in range(d0, d0 + self.max_consecutive_away + 1)
                            for o in range(self.num_teams) if o != t)
                        <= self.max_consecutive_away
                    )

        # --- Modélisation des breaks (matchs consécutifs à domicile ou à l'extérieur).
        # Pour chaque équipe et chaque journée, on définit des variables indicatrices.
        is_home = {}
        is_away = {}
        for t in range(self.num_teams):
            for d in range(self.num_days):
                home_expr = sum(self.X.get((t, o, d), 0)
                                for o in range(self.num_teams) if o != t)
                away_expr = sum(self.X.get((o, t, d), 0)
                                for o in range(self.num_teams) if o != t)
                is_home[t, d] = model.NewBoolVar(f"is_home_{t}_day{d}")
                is_away[t, d] = model.NewBoolVar(f"is_away_{t}_day{d}")
                model.Add(home_expr == is_home[t, d])
                model.Add(away_expr == is_away[t, d])

        # Définir une variable de break pour chaque équipe entre deux journées consécutives.
        B = {}
        total_breaks = {}
        for t in range(self.num_teams):
            for d in range(self.num_days - 1):
                b = model.NewBoolVar(f"break_{t}_day{d}")
                B[t, d] = b
                # b vaut 1 si le statut (domicile ou extérieur) est le même pour la journée d et d+1.
                home_break = model.NewBoolVar(f"home_break_{t}_{d}")
                away_break = model.NewBoolVar(f"away_break_{t}_{d}")
                model.AddBoolAnd([is_home[t, d], is_home[t, d + 1]]).OnlyEnforceIf(home_break)
                model.AddBoolOr([is_home[t, d].Not(), is_home[t, d + 1].Not()]).OnlyEnforceIf(home_break.Not())
                model.AddBoolAnd([is_away[t, d], is_away[t, d + 1]]).OnlyEnforceIf(away_break)
                model.AddBoolOr([is_away[t, d].Not(), is_away[t, d + 1].Not()]).OnlyEnforceIf(away_break.Not())
                model.AddMaxEquality(b, [home_break, away_break])
            total_breaks[t] = model.NewIntVar(0, self.num_days, f"total_breaks_{t}")
            model.Add(total_breaks[t] == sum(B[t, d] for d in range(self.num_days - 1)))
        global_breaks = model.NewIntVar(0, self.num_teams * (self.num_days - 1), "global_breaks")
        model.Add(global_breaks == sum(total_breaks[t] for t in range(self.num_teams)))
        # Utilisation d'une inégalité pour autoriser quelques marges.
        model.Add(global_breaks == max_total_breaks)

        # --- Objectif : ici on minimise le nombre total de breaks.
        # model.Minimize(global_breaks)

        # --- Résolution.
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        result = solver.Solve(model)

        self.solver = solver
        self.model_obj = model

        self.schedule = []
        if result in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for d in range(self.num_days):
                matches = []
                for i in range(self.num_teams):
                    for j in range(self.num_teams):
                        if i != j and (i, j, d) in self.X and solver.Value(self.X[(i, j, d)]) == 1:
                            matches.append((i, j))
                self.schedule.append(matches)
        else:
            self.schedule = None

    def print_schedule(self):
        if self.schedule is None:
            print("Aucun calendrier valide n'a été trouvé.")
        else:
            for day, matches in enumerate(self.schedule, start=1):
                date_str = (self.start_date + timedelta(days=day - 1)).strftime("%Y-%m-%d")
                print(f"Journée {day} ({date_str}) :")
                for (home_idx, away_idx) in matches:
                    print(f"  {self.teams[home_idx].name} (domicile) vs {self.teams[away_idx].name} (extérieur)")

# Exemple d'utilisation
if __name__ == "__main__":
    nb_teams = 12
    stadiums = [Stadium(f"Stade {i + 1}") for i in range(nb_teams)]
    teams = [Team(f"Équipe {chr(65 + i)}", stadiums[i]) for i in range(nb_teams)]
    schedule = Schedule(
        teams,
        start_date="2025-04-01",
        max_consecutive_away=2,
        max_total_breaks=len(teams) - 2
    )
    schedule.print_schedule()
