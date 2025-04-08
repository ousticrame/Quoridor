package fr.matthieufouliard.repository;

import jakarta.enterprise.context.ApplicationScoped;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@ApplicationScoped
public class Players {
    private final Map<UUID, String> players;

    public Players() {
        this.players = new HashMap<>();
    }

    public UUID createPlayer(String username) {
        UUID UUID = java.util.UUID.randomUUID();
        this.players.put(UUID, username.trim());
        return UUID;
    }

    public String getUsername(UUID UUID) {
        return this.players.get(UUID);
    }
}
