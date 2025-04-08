package fr.matthieufouliard.model.Request;

import fr.matthieufouliard.model.TurnStart;

public class CreateGameRequest {
    public Integer size;
    public Integer nbWalls;
    public TurnStart turnStart;

    @Override
    public String toString() {
        return "{\n" +
                "size: " + this.size + "\n" +
                "nbWalls: " + this.nbWalls + "\n" +
                "turnStart: " + this.turnStart + "\n" +
                "}";
    }
}
