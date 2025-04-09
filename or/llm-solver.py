from datetime import datetime, timedelta
from openai import OpenAI
from ortools.sat.python import cp_model
import json
from conf import api_key

# ========== DATA CLASSES ==========

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

# ========== SOLVER ==========

class Schedule:
    def __init__(self, teams, start_date, max_consecutive_away):
        if len(teams) % 2 == 1:            
            teams.append(Team(f"Equipe repos",Stadium(f"Stade repos")))
        self.teams = teams
        self.start_date = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        self.max_consecutive_away = max_consecutive_away
        self.num_teams = len(teams)
        self.num_days = self.num_teams - 1
        model = cp_model.CpModel()

        valid_days = {
            t: [d for d in range(self.num_days)
                if teams[t].stadium.is_available_on(self.start_date + timedelta(days=d))]
            for t in range(self.num_teams)
        }

        self.X = {}
        for i in range(self.num_teams):
            for j in range(self.num_teams):
                if i == j:
                    continue
                for d in valid_days[i]:
                    self.X[(i, j, d)] = model.NewBoolVar(f"match_{i}_{j}_day{d+1}")

        for i in range(self.num_teams):
            for j in range(i + 1, self.num_teams):
                model.Add(
                    sum(self.X.get((i, j, d), 0) for d in range(self.num_days)) +
                    sum(self.X.get((j, i, d), 0) for d in range(self.num_days))
                    == 1
                )

        for t in range(self.num_teams):
            for d in range(self.num_days):
                model.Add(
                    sum(self.X.get((t, o, d), 0) for o in range(self.num_teams) if o != t) +
                    sum(self.X.get((o, t, d), 0) for o in range(self.num_teams) if o != t)
                    == 1
                )

        for t in range(self.num_teams):
            for d0 in range(self.num_days - self.max_consecutive_away):
                model.Add(
                    sum(self.X.get((o, t, d), 0)
                        for d in range(d0, d0 + self.max_consecutive_away + 1)
                        for o in range(self.num_teams) if o != t)
                    <= self.max_consecutive_away
                )

        is_home = {}
        is_away = {}
        for t in range(self.num_teams):
            for d in range(self.num_days):
                home_expr = sum(self.X.get((t, o, d), 0) for o in range(self.num_teams) if o != t)
                away_expr = sum(self.X.get((o, t, d), 0) for o in range(self.num_teams) if o != t)
                is_home[t, d] = model.NewBoolVar(f"is_home_{t}_day{d}")
                is_away[t, d] = model.NewBoolVar(f"is_away_{t}_day{d}")
                model.Add(home_expr == is_home[t, d])
                model.Add(away_expr == is_away[t, d])

        B = {}
        total_breaks = {}
        for t in range(self.num_teams):
            for d in range(self.num_days - 1):
                b = model.NewBoolVar(f"break_{t}_day{d}")
                B[t, d] = b
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
        model.Minimize(global_breaks)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 360
        result = solver.Solve(model)

        self.total_breaks_value = solver.Value(global_breaks)
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

# ========== FUNCTION CALL FOR GPT ==========

def solve_schedule(num_teams: int, start_date: str, max_consecutive_away: int) -> str:
    stadiums = [Stadium(f"Stadium {i + 1}") for i in range(num_teams)]
    teams = [Team(f"Team {chr(65 + i)}", stadiums[i]) for i in range(num_teams)]

    schedule = Schedule(teams, start_date, max_consecutive_away)

    if schedule.schedule is None:
        return "No feasible schedule found."

    output = ""
    for day, matches in enumerate(schedule.schedule, start=1):
        date_str = (schedule.start_date + timedelta(days=day - 1)).strftime("%Y-%m-%d")
        output += f"Day {day} ({date_str}):\n"
        for home, away in matches:
            output += f"  {teams[home].name} (home) vs {teams[away].name} (away)\n"

    output += f"\nTotal number of breaks: {schedule.total_breaks_value}\n"
    return output

# ========== EXAMPLE GPT FUNCTION CALL ==========

if __name__ == "__main__":
    client = OpenAI(api_key)

    functions = [ {
        "name": "solve_schedule",
        "description": "Generate a football round-robin schedule minimizing breaks",
        "parameters": {
            "type": "object",
            "properties": {
                "num_teams": {"type": "integer"},
                "start_date": {"type": "string"},
                "max_consecutive_away": {"type": "integer"}
            },
            "required": ["num_teams", "start_date", "max_consecutive_away"]
        }
    }]

    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[{
            "role": "user",
            "content": "Generate a tournament with 20 teams starting on 2025-04-01, and no more than 2 away games in a row."
        }],
        functions=functions,
        function_call={"name": "solve_schedule"}
    )

    if response.choices[0].message.function_call:
        args = json.loads(response.choices[0].message.function_call.arguments)
        result = solve_schedule(**args)
        print(result)