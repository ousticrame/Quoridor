import { useState, useEffect, useRef } from "react";
import GameBoard from "./components/GameBoard";
import GameControls from "./components/GameControls";
import "./App.css";
import { GameState } from "./utils/types";
import { MinesweeperAPI } from "./utils/backend";

const DEFAULT_COLS = 10;
const DEFAULT_ROWS = 10;
const DEFAULT_MINES = 10;

function App() {
  const [gameId, setGameId] = useState<string | null>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const timerRef = useRef<number | null>(null);

  // Stop the timer when game is over or reset
  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  // Start the timer
  const startTimer = () => {
    // Stop any existing timer first
    stopTimer();

    // Start a new interval timer
    timerRef.current = setInterval(() => {
      setElapsedTime((prevTime) => prevTime + 1);
    }, 1000);
  };

  const startNewGame = async (cols: number, rows: number, mines: number) => {
    try {
      console.log("Starting new game...");
      const { game_id, state } = await MinesweeperAPI.startNewGame(
        cols,
        rows,
        mines
      );

      console.log("Game started:", { game_id, state });
      setGameId(game_id);
      setGameState(state);
      setError(null);

      // Reset elapsed time and start timer
      setElapsedTime(0);
      startTimer();
    } catch (error) {
      console.error("Error starting new game:", error);
      setError("Failed to start new game. Is the backend running?");
      stopTimer();
    }
  };

  const handleCellClick = async (x: number, y: number) => {
    if (!gameId || !gameState) return;

    try {
      const { state } = await MinesweeperAPI.revealCell(gameId, x, y);
      setGameState(state);

      // Stop timer if game is over
      if (state.game_over) {
        stopTimer();
      }
    } catch (error) {
      console.error("Error revealing cell:", error);
    }
  };

  const handleCellRightClick = async (x: number, y: number) => {
    if (!gameId || !gameState) return;

    try {
      const { state } = await MinesweeperAPI.toggleFlag(gameId, x, y);
      setGameState(state);
    } catch (error) {
      console.error("Error toggling flag:", error);
    }
  };

  const handleSolveMove = async () => {
    if (!gameId || !gameState) return;

    try {
      // Get next move
      const moveData = await MinesweeperAPI.getSolveNextMove(gameId);

      if (moveData.error) {
        console.error("No moves available");
        return;
      }

      // Apply the move
      const { state } = await MinesweeperAPI.applySolveMove(gameId);
      setGameState(state);

      // Stop timer if game is over
      if (state.game_over) {
        stopTimer();
      }
    } catch (error) {
      console.error("Error solving move:", error);
    }
  };

  // Clean up timer on component unmount
  useEffect(() => {
    console.log("App mounted, starting new game...");
    startNewGame(DEFAULT_COLS, DEFAULT_ROWS, DEFAULT_MINES);

    return () => {
      stopTimer();
    };
  }, []);

  if (error) {
    return (
      <div className="app">
        <h1>Minesweeper</h1>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="app">
      <h1>Minesweeper</h1>
      <GameControls
        onNewGame={(cols, rows, mines) => startNewGame(cols, rows, mines)}
        onSolveMove={handleSolveMove}
        mineCount={gameState?.num_mines || 0}
        gameStatus={
          gameState?.game_over
            ? gameState.won
              ? "Won!"
              : "Game Over"
            : "Playing"
        }
        elapsedTime={elapsedTime}
      />
      {gameState ? (
        <GameBoard
          grid={gameState.grid}
          revealed={gameState.revealed}
          flagged={gameState.flagged}
          onCellClick={handleCellClick}
          onCellRightClick={handleCellRightClick}
          disabled={gameState?.game_over}
        />
      ) : (
        <div>Loading game...</div>
      )}
    </div>
  );
}

export default App;
