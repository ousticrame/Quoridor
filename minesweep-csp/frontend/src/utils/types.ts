export interface GameState {
  grid: number[][];
  revealed: boolean[][];
  flagged: boolean[][];
  game_over: boolean;
  won: boolean;
  width: number;
  height: number;
  num_mines: number;
  start_time?: number; // Optional start time
}
