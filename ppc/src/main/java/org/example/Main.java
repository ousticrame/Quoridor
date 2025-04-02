package org.example;

public class Main {
    public static void main(String[] args) {
        RoundRobinScheduler.run();
        System.out.println("RunWithRest");
        RoundRobinScheduler.runWithRest();
    }
}