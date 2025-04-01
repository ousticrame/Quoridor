from ortools.sat.python import cp_model
from typing import List, Dict, Callable, Optional


def student_project_allocation(
    students: List[int],
    projects: List[int],
    preferences: Dict[int, List[int]],
    project_capacities: Dict[int, int],
    constraints: Optional[List[Callable]] = None,
) -> Optional[Dict[int, int]]:
    """
    Solves the student project allocation problem using OR-Tools CP-SAT (no supervisors).

    Args:
        students: A list of student IDs (e.g., [1, 2, 3]).
        projects: A list of project IDs (e.g., [101, 102, 103]).
        preferences: A dictionary mapping student ID to a list of preferred project IDs
                     (e.g., {1: [101, 102], 2: [103, 101]}).
        project_capacities: A dictionary mapping project ID to its maximum capacity
                           (e.g., {101: 2, 102: 1, 103: 2}).
        constraints: A list of constraint functions.  Each constraint function should
                     take the model, students, projects, assignments as input
                     and add constraints to the model accordingly.  Defaults to None.

    Returns:
        A dictionary mapping student ID to assigned project ID, or None if no solution is found.
    """
    
    print("students:", students)
    print("projects:", projects)
    print("preferences:", preferences)
    print("project_capacities:", project_capacities)
    print("constraints:", constraints)

    model = cp_model.CpModel()

    # Create variables: assignment[student, project] = 1 if student is assigned to project.
    assignments: Dict[tuple[int, int], cp_model.IntVar] = {}
    for student in students:
        for project in projects:
            assignments[(student, project)] = model.NewBoolVar(
                f"assignment_s{student}_p{project}"
            )

    # Constraint 1: Each student is assigned to exactly one project.
    for student in students:
        model.Add(sum(assignments[(student, project)] for project in projects) == 1)

    # Constraint 2: Project capacities are respected.
    for project in projects:
        model.Add(
            sum(assignments[(student, project)] for student in students)
            <= project_capacities[project]
        )

    # Constraint 3: Only assign projects that are in the student's preferences.  Important to do this
    # BEFORE the objective function is applied.
    for student in students:
        preferred_projects = preferences.get(
            student, []
        )  # Get preferred projects, default to [] if none defined.
        for project in projects:
            if project not in preferred_projects:
                model.Add(assignments[(student, project)] == 0)  # Cannot be assigned.

    # Custom constraints (optional).  Constraints are passed in as functions that take the model,
    # students, projects, the assignment map.  Constraints are passed in as
    # function pointers and must be designed in advanced.
    if constraints:
        for constraint_function in constraints:
            constraint_function(model, students, projects, assignments)

    # Objective function: Maximize the satisfaction of student preferences (optional).
    # This example assumes the order in the preferences list represents the satisfaction level
    # (higher index = lower satisfaction).  You can modify this to suit your needs.
    objective_terms = []
    for student in students:
        preferred_projects = preferences.get(student, [])
        for i, project in enumerate(preferred_projects):
            # Higher preference order yields a higher score.  Scale the values to make them
            # meaningfully bigger than 1 to promote satisfying all the preferences (as opposed
            # to leaving some students unassigned but partially satisfying others).
            priority = (
                len(preferred_projects) - i
            )  # Reversed to score higher for more preferred
            objective_terms.append(
                cp_model.LinearExpr.Term(
                    assignments[(student, project)], priority * 100
                )
            )

    model.Maximize(sum(objective_terms))

    # Solve the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution found!")
        allocation: Dict[int, int] = {}
        for student in students:
            for project in projects:
                if solver.Value(assignments[(student, project)]) == 1:
                    allocation[student] = project
                    break  # Each student is assigned to only one project.
        return allocation
    else:
        print("No solution found.")
        return None


# Example usage:
if __name__ == "__main__":
    students = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    projects = [101, 102, 103, 104, 105]

    preferences = {
        1: [101, 102, 103],
        2: [102, 104, 101],
        3: [103, 101, 104],
        4: [104, 103, 102],
        5: [101, 104, 102],
        6: [102, 101, 103],
        7: [105, 101, 102],
        8: [103, 105, 104],
        9: [104, 102, 105],
        10: [101, 103, 105],
    }

    project_capacities = {101: 2, 102: 2, 103: 1, 104: 2, 105: 2}

    def example_constraint(model, students, projects, assignments):
        # Example custom constraint 1: Student 1 and 2 cannot be on the same project
        for project in projects:
            model.Add(assignments[(1, project)] + assignments[(2, project)] <= 1)

        # Example custom constraint 2:  If student 3 is on project 101, then student 4 must be on project 102
        model.AddBoolOr([assignments[(3, 101)].Not(), assignments[(4, 102)]])

        # Example custom constraint 3: Ensure at least one of students 5, 6, or 7 is assigned to project 105
        model.Add(sum(assignments[(s, 105)] for s in [5, 6, 7]) >= 1)

    allocation = student_project_allocation(
        students,
        projects,
        preferences,
        project_capacities,
        constraints=[example_constraint],  # Pass custom constraints here.
    )

    if allocation:
        for student, project in allocation.items():
            print(f"Student {student} is assigned to project {project}")
