<template>
  <div id="app" style="text-align: center">
    <h1>AI Wordle Solver</h1>
    <div>
      <button @click="startNewGame" style="margin-right: 10px">New Game</button>
      <button @click="solve" :disabled="solved" style="margin-right: 10px">
        Solve
      </button>
      <button @click="nextSolverStep" :disabled="solved">Next Move</button>
    </div>

    <div v-if="loading" class="spinner"></div>

    <div v-if="targetWord">Word to guess: {{ targetWord }}</div>
    <div v-if="guesses.length" class="result">
      Solved {{ targetWord }} in {{ guesses.length }} attempts!
    </div>
    <WordleBoard
      :guesses="guesses"
      :feedback="feedback"
      :nbPossibleWords="nbPossibleWords"
      :move="move"
    />
  </div>
</template>

<script>
import axios from "axios";
import WordleBoard from "./components/WordleBoard.vue";

export default {
  components: { WordleBoard },
  data() {
    return {
      targetWord: "",
      guesses: [],
      feedback: [],
      solved: false,
      nbPossibleWords: 0,
      move: 0,
      loading: false,
    };
  },
  methods: {
    async startNewGame() {
      const response = await axios.post("http://localhost:5000/new-game");
      this.targetWord = response.data.target_word;
      this.guesses = [];
      this.feedback = [];
      this.solved = false;
      this.move = 0;
    },
    async solve() {
      this.loading = true;
      try {
        const response = await axios.get("http://localhost:5000/solver-guess");
        this.guesses = response.data.guesses;
        this.feedback = response.data.feedback;
        this.nbPossibleWords = response.data.nb_possible_words;
        this.solved = response.data.solved;
      } finally {
        this.loading = false;
      }
    },
    nextSolverStep() {
      this.move++;
    },
  },
};
</script>

<style>
.spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
