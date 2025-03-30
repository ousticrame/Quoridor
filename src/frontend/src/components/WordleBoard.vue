<template>
  <div class="grid-wrapper">
    <div
      v-if="guesses.length > 0 && feedback.length > 0"
      class="grid-container"
    >
      <div v-for="(guess, index) in guesses" :key="index" class="guess-row">
        <div class="tiles-container">
          <div
            v-for="(letter, letterIndex) in guess"
            :key="letterIndex"
            class="letter-tile"
            :class="
              index < move ? feedbackClasses[index][letterIndex] : 'gray-tile'
            "
          >
            {{ index < move ? letter : " " }}
          </div>
        </div>
        <div class="possible-words-count">
          {{ index < move ? nbPossibleWords[index] || "" : " " }}
        </div>
      </div>
    </div>
    <div v-else class="grid-container">
      <div v-for="i in 5" :key="i" class="guess-row">
        <div class="tiles-container">
          <div v-for="i in 5" :key="i" class="letter-tile gray-tile">
            {{ " " }}
          </div>
        </div>
        <div class="possible-words-count"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    guesses: Array,
    feedback: Array,
    nbPossibleWords: Array,
    move: Number,
  },
  computed: {
    feedbackClasses() {
      return this.feedback.map((row) =>
        row.map((status) => ({
          "green-tile": status === "G",
          "yellow-tile": status === "Y",
          "gray-tile": status === "B",
        }))
      );
    },
  },
};
</script>

<style>
.grid-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
  margin-left: 100px;
}

.grid-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.guess-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
}

.tiles-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
}

.letter-tile {
  width: 60px;
  height: 60px;
  border: 2px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2em;
}

.possible-words-count {
  min-width: 80px;
  font-weight: bold;
  color: black;
  text-align: left;
}

.green-tile {
  background-color: #6aaa64;
  color: black;
}

.yellow-tile {
  background-color: #c9b458;
  color: black;
}

.gray-tile {
  background-color: #787c7e;
  color: black;
}
</style>
