let size;
let walls;
let positions;
let nbWalls;
let turn;
let usernames;
let winner;
let winnerIsDisplayed = false;
let isYourTurn;

const turnToInteger = {
    PLAYER_1: 0,
    PLAYER_2: 1
};

const oppositeDirection = {
    UP: 'DOWN',
    RIGHT: 'LEFT',
    DOWN: 'UP',
    LEFT: 'RIGHT'
};

const directionToIsWall = {
    UP: isWallUp,
    RIGHT: isWallRight,
    DOWN: isWallDown,
    LEFT: isWallLeft
};

const directionToCoordinate = {
    UP: { x: -1, y: 0 },
    RIGHT: { x: 0, y: 1 },
    DOWN: { x: 1, y: 0 },
    LEFT: { x: 0, y: -1 },
}

function coordinateToDirection(coordinate) {
    for (let direction of ["UP", "RIGHT", "DOWN", "LEFT"]) {
        if (coordinate.x === directionToCoordinate[direction].x && coordinate.y === directionToCoordinate[direction].y) {
            return direction;
        }
    }

    return undefined;
}

function isInBoard(position) {
    return position.x >= 0 && position.x < size &&
           position.y >= 0 && position.y < size;
}

function isWallUp(coordinate) {
    if (coordinate.x !== 0 && coordinate.y !== 0 &&
        walls[coordinate.x - 1][coordinate.y - 1] === 'HORIZONTAL') {
        return true;
    }

    return coordinate.x !== 0 && coordinate.y !== size - 1 &&
        walls[coordinate.x - 1][coordinate.y] === 'HORIZONTAL';
}

function isWallRight(coordinate) {
    if (coordinate.x !== 0 && coordinate.y !== size - 1 &&
        walls[coordinate.x - 1][coordinate.y] === 'VERTICAL') {
        return true;
    }

    return coordinate.x !== size - 1 && coordinate.y !== size - 1 &&
        walls[coordinate.x][coordinate.y] === 'VERTICAL';
}

function isWallDown(coordinate) {
    if (coordinate.x !== size - 1 && coordinate.y !== size - 1 &&
        walls[coordinate.x][coordinate.y] === 'HORIZONTAL') {
        return true;
    }

    return coordinate.x !== size - 1 && coordinate.y !== 0 &&
        walls[coordinate.x][coordinate.y - 1] === 'HORIZONTAL';
}

function isWallLeft(coordinate) {
    if (coordinate.x !== size - 1 && coordinate.y !== 0 &&
        walls[coordinate.x][coordinate.y - 1] === 'VERTICAL') {
        return true;
    }

    return coordinate.x !== 0 && coordinate.y !== 0 &&
        walls[coordinate.x - 1][coordinate.y - 1] === 'VERTICAL';
}

function canSimpleMove(position, direction) {
    if (directionToIsWall[direction](position)) return false;

    const dir = directionToCoordinate[direction];
    const projectionPosition = { x: position.x + dir.x, y: position.y + dir.y };

    return isInBoard(projectionPosition);
}

function canMove(direction, jump) {
    const current = positions[turnToInteger[turn]];
    const provisional = { ...current };
    const opponent = positions[(turnToInteger[turn] + 1) % 2];

    if (jump) {
        const difference = { x: opponent.x - provisional.x, y: opponent.y - provisional.y };

        if (difference.x * difference.x + difference.y * difference.y !== 1) return false;

        const differenceDirection = coordinateToDirection(difference);
        if (oppositeDirection[differenceDirection] === direction) return false;
        if (directionToIsWall[differenceDirection](provisional)) return false;

        provisional.x += difference.x;
        provisional.y += difference.y;

        if (canSimpleMove(provisional, differenceDirection)) return differenceDirection === direction;
    }

    if (!canSimpleMove(provisional, direction))
        return false;
    provisional.x = provisional.x + directionToCoordinate[direction].x
    provisional.y = provisional.y + directionToCoordinate[direction].y

    return (provisional.x !== opponent.x || provisional.y !== opponent.y);
}

async function move(direction, jump) {
    if (jump) {
        positions[turnToInteger[turn]].x = positions[(turnToInteger[turn] + 1) % 2].x;
        positions[turnToInteger[turn]].y = positions[(turnToInteger[turn] + 1) % 2].y;
    }
    positions[turnToInteger[turn]].x = positions[turnToInteger[turn]].x + directionToCoordinate[direction].x;
    positions[turnToInteger[turn]].y = positions[turnToInteger[turn]].y + directionToCoordinate[direction].y;
    isYourTurn = false;
    display();
    const gameID = new URLSearchParams(window.location.search).get("uuid");
    const response = await fetch(`${backendURL}/game/${gameID}/move`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        },
        body: JSON.stringify({
            direction,
            jump
        })
    });
    if (!response.ok) {
        location.reload();
    }
}

function isInWallMap(position) {
    return position.x >= 0 && position.x < size - 1 &&
           position.y >= 0 && position.y < size - 1;
}

function cloneBoardState() {
    return {
        size,
        walls: walls.map(row => [...row]),
        positions: positions.map(p => ({ ...p })),
        nbWalls: [...nbWalls],
        turn
    };
}

function restoreBoardState(state) {
    size = state.size;
    walls = state.walls.map(row => [...row]);
    positions = state.positions.map(p => ({ ...p }));
    nbWalls = [...state.nbWalls];
    turn = state.turn;
}

function canWin() {
    for (let i = 0; i < 2; i++) {
        let canPlayerWin = false;
        const mark = Array.from({ length: size }, () =>
            Array.from({ length: size }, () => false)
        );

        const queue = [positions[i]];
        mark[positions[i].x][positions[i].y] = true;

        while (queue.length > 0) {
            const position = queue.shift();
            if (position.x === i * (size - 1)) {
                canPlayerWin = true;
                break;
            }

            for (const dir in directionToCoordinate) {
                if (canSimpleMove(position, dir)) {
                    const delta = directionToCoordinate[dir];
                    const newPos = { x: position.x + delta.x, y: position.y + delta.y };
                    if (!mark[newPos.x][newPos.y]) {
                        queue.push(newPos);
                        mark[newPos.x][newPos.y] = true;
                    }
                }
            }
        }

        if (!canPlayerWin) return false;
    }

    return true;
}

function canPlace(position, wall) {
    if (!isInWallMap(position) || wall === 'NONE') return false;
    if (nbWalls[turnToInteger[turn]] <= 0) return false;
    if (walls[position.x][position.y] !== 'NONE') return false;
    if (winner !== "NONE") return false;
    if (!isYourTurn) return false
    if (document.getElementById(`player-${turnToInteger[turn] + 1}`).classList.contains("selected")) return false;
    if (usernames[0] == null || usernames[1] == null) return false

    const savedState = cloneBoardState();
    walls[position.x][position.y] = wall;
    const valid = canWin();
    restoreBoardState(savedState);
    if (!valid) return false;

    if (wall === 'HORIZONTAL') {
        const left = position.y !== 0 && walls[position.x][position.y - 1] === 'HORIZONTAL';
        const right = position.y !== size - 2 && walls[position.x][position.y + 1] === 'HORIZONTAL';
        return !(left || right);
    } else {
        const up = position.x !== 0 && walls[position.x - 1][position.y] === 'VERTICAL';
        const down = position.x !== size - 2 && walls[position.x + 1][position.y] === 'VERTICAL';
        return !(up || down);
    }
}

async function place(x, y, wall, alt) {
    if (canPlace({x: x, y: y}, wall)) {
        nbWalls[turnToInteger[turn]] = nbWalls[turnToInteger[turn]] - 1;
        walls[x][y] = wall;
        isYourTurn = false;
        display();
        const gameID = new URLSearchParams(window.location.search).get("uuid");
        const response = await fetch(`${backendURL}/game/${gameID}/place`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Player-UUID": sessionStorage.getItem("playerID")
            },
            body: JSON.stringify({
                x,
                y,
                wall,
            })
        });
        if (!response.ok) {
            location.reload();
        }
    }
    else if (alt !== null) {
        if (alt === "HORIZONTAL" || alt === "VERTICAL")
        {
            wall = alt;
        }
        else if (wall === "HORIZONTAL") {
            y = y + alt;
        }
        else {
            x = x + alt
        }
        if (canPlace({x: x, y: y}, wall)) {
            nbWalls[turnToInteger[turn]] = nbWalls[turnToInteger[turn]] - 1;
            walls[x][y] = wall;
            isYourTurn = false;
            display();
            const gameID = new URLSearchParams(window.location.search).get("uuid");
            const response = await fetch(`${backendURL}/game/${gameID}/place`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Player-UUID": sessionStorage.getItem("playerID")
                },
                body: JSON.stringify({
                    x,
                    y,
                    wall,
                })
            });
            if (!response.ok) {
                location.reload();
            }
        }
    }
}

function select(x, y) {
    const player = document.getElementById(`player-${turnToInteger[turn] + 1}`);
    const cell = document.getElementById(`cell-${x}-${y}`);
    const position = positions[turnToInteger[turn]];

    if (winner !== "NONE") return;
    if (!isYourTurn) return;
    if (usernames[0] == null || usernames[1] == null) return false

    if (player.classList.contains("selected")) {
        if (cell.classList.contains("selected")) {
            deSelect();
            if ((position.x - x) ** 2 + (position.y - y) ** 2 === 1) {
                coordinate = positions[(turnToInteger[turn]) % 2];
            }
            else {
                coordinate = positions[(turnToInteger[turn] + 1) % 2];
            }
            coordinate = { x: x - coordinate.x, y: y - coordinate.y};
            move(coordinateToDirection(coordinate), (position.x - x) ** 2 + (position.y - y) ** 2 !== 1)
        }
        else {
            deSelect();
        }
    }
    else {
        if (x === position.x && y === position.y) {
            if (!player.classList.contains("selected")) {
                player.className = player.className + " selected";
            }

            for (let direction of ["UP", "RIGHT", "DOWN", "LEFT"]) {
                if (canMove(direction, true)) {
                    coordinate = positions[(turnToInteger[turn] + 1) % 2];
                    dir = directionToCoordinate[direction];
                    coordinate = { x: coordinate.x + dir.x, y: coordinate.y + dir.y };
                    const selectedCell = document.getElementById(`cell-${coordinate.x}-${coordinate.y}`);
                    if (!selectedCell.classList.contains("selected")) {
                        selectedCell.className = selectedCell.className + " selected";
                    }
                }
                if (canMove(direction, false)) {
                    coordinate = positions[turnToInteger[turn]];
                    dir = directionToCoordinate[direction];
                    coordinate = { x: coordinate.x + dir.x, y: coordinate.y + dir.y };
                    const selectedCell = document.getElementById(`cell-${coordinate.x}-${coordinate.y}`);
                    if (!selectedCell.classList.contains("selected")) {
                        selectedCell.className = selectedCell.className + " selected";
                    }
                }
            }
        }
    }
}

function deSelect() {
    const elements = Array.from(document.getElementsByClassName("selected"));
    elements.forEach(element => element.classList.remove("selected"));
}

function hoverWall(x, y, wall, alt) {
    if (canPlace({ x: x, y: y }, wall)) {
        let walls = Array.from(document.getElementsByClassName(`${wall.toLowerCase(wall)}-wall-${x}-${y}`));
        walls.forEach(wall => { if (!wall.classList.contains("hovered")) wall.className = wall.className + " hovered" })
        corner = document.getElementById(`corner-${x}-${y}`);
        if (!corner.classList.contains("hovered")) {
            corner.className = corner.className + " hovered";
        }
    }
    else if (alt !== null) {
        if (alt === "HORIZONTAL" || alt === "VERTICAL")
        {
            wall = alt;
        }
        else if (wall === "HORIZONTAL") {
            y = y + alt;
        }
        else {
            x = x + alt
        }
        if (canPlace({ x: x, y: y }, wall)) {
            let walls = Array.from(document.getElementsByClassName(`${wall.toLowerCase(wall)}-wall-${x}-${y}`));
            walls.forEach(wall => { if (!wall.classList.contains("hovered")) wall.className = wall.className + " hovered" })
            corner = document.getElementById(`corner-${x}-${y}`);
            if (!corner.classList.contains("hovered")) {
                corner.className = corner.className + " hovered";
            }
        }
    }
}

function deHoverWall() {
    Array.from(document.getElementsByClassName("horizontal-wall")).forEach(horizontalWall => horizontalWall.classList.remove("hovered"));
    Array.from(document.getElementsByClassName("vertical-wall")).forEach(verticalWall => verticalWall.classList.remove("hovered"));
    Array.from(document.getElementsByClassName("corner")).forEach(corner => corner.classList.remove("hovered"));
}

function createCell(x, y) {
    const element = document.createElement("div");
    element.className = "cell";
    element.id = `cell-${x}-${y}`;
    element.addEventListener("click", () => select(x, y))
    return element;
}

function createHorizontalWall(x, y) {
    const element = document.createElement("div");
    element.className = "horizontal-wall";
    for (let i = 0; i < 2; i++) {
        const innerWall = document.createElement("div");
        innerWall.className = "half-horizontal-wall";
        innerWall.addEventListener("click", () => place(x, y - 1 + i, "HORIZONTAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseenter", () => hoverWall(x, y - 1 + i, "HORIZONTAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseleave", () => deHoverWall());
        element.appendChild(innerWall);
    }
    if (y == 0) {
        element.className = element.className + ` horizontal-wall-${x}-${y}`
    }
    else if (y == size - 1) {
        element.className = element.className + ` horizontal-wall-${x}-${y - 1}`
    }
    else {
        element.className = element.className + ` horizontal-wall-${x}-${y} horizontal-wall-${x}-${y - 1}`
    }
    return element;
}

function createVerticalWall(x, y) {
    const element = document.createElement("div");
    element.className = "vertical-wall";
    for (let i = 0; i < 2; i++) {
        const innerWall = document.createElement("div");
        innerWall.className = "half-vertical-wall";
        innerWall.addEventListener("click", () => place(x - 1 + i, y, "VERTICAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseenter", () => hoverWall(x - 1 + i, y, "VERTICAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseleave", () => deHoverWall());
        element.appendChild(innerWall);
    }
    if (x == 0) {
        element.className = element.className + ` vertical-wall-${x}-${y}`
    }
    else if (x == size - 1) {
        element.className = element.className + ` vertical-wall-${x - 1}-${y}`
    }
    else {
        element.className = element.className + ` vertical-wall-${x}-${y} vertical-wall-${x - 1}-${y}`
    }
    
    return element;
}

function createCorner(x, y) {
    const element = document.createElement("div");
    element.className = "corner";
    element.id = `corner-${x}-${y}`
    element.wall = "none";

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("viewBox", "0 0 100 100");
  
    const triangles = [
        { points: "0,0 100,0 50,50", direction: "VERTICAL" },
        { points: "100,0 100,100 50,50", direction: "HORIZONTAL" },
        { points: "100,100 0,100 50,50", direction: "VERTICAL" },
        { points: "0,100 0,0 50,50", direction: "HORIZONTAL" }
    ];
  
    for (const triangle of triangles) {
        const polygon = document.createElementNS(svgNS, "polygon");
        polygon.setAttribute("points", triangle.points);
        polygon.addEventListener("click", () => place(x, y, triangle.direction, triangle.direction === "VERTICAL" ? "HORIZONTAL" : "VERTICAL" ));
        polygon.addEventListener("mouseenter", () => hoverWall(x, y, triangle.direction, triangle.direction === "VERTICAL" ? "HORIZONTAL" : "VERTICAL" ));
        polygon.addEventListener("mouseleave", () => deHoverWall());
        svg.appendChild(polygon);
    }

    element.appendChild(svg);

    return element;
}

createElement = [createCell, createVerticalWall, createHorizontalWall, createCorner];

async function refresh() {
    const gameID = new URLSearchParams(window.location.search).get("uuid");
    const response = await fetch(`${backendURL}/game/${gameID}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        }
    });
    if (!response.ok) {
        document.location.href = "../games";
        return;
    }

    const json = await response.json();
    size = json.board.size;
    walls = json.board.walls;
    positions = json.board.positions;
    nbWalls = json.board.nbWalls;
    turn = json.board.turn;
    usernames = json.usernames;
    winner = json.winner;
    isYourTurn = json.isYourTurn;
}

function generate() {
    const gameBoard = document.getElementById("game-board");

    gameBoard.style.gridTemplateColumns = `repeat(${size * 2 - 1}, auto)`;
    gameBoard.style.gridTemplateRows = `repeat(${size * 2 - 1}, auto)`;

    for (let i = 0; i < size * 2 - 1; i++) {
        for (let j = 0; j < size * 2 - 1; j++) {
            gameBoard.appendChild(createElement[i % 2 * 2 + j % 2](Math.floor(i / 2), Math.floor(j / 2)));
        }
    }

    positions.forEach((pos, index) => {
        const cell = document.getElementById(`cell-${pos.x}-${pos.y}`);
        const player = document.createElement("div");
        player.className = `player`;
        player.id = `player-${index + 1}`;
        cell.appendChild(player);

        const image = document.createElement("img");
        image.src = `../player_${index + 1}.png`;
        image.alt = `player_1`;
        player.appendChild(image);
    });
}

function display() {
    positions.forEach((position, index) => {
        const cell = document.getElementById(`cell-${position.x}-${position.y}`);
        cell.appendChild(document.getElementById(`player-${index + 1}`));
    });

    Array.from(document.getElementsByClassName("placed")).forEach(wall => wall.classList.remove("placed"));

    for (i = 0; i < size - 1; i++) {
        for (j = 0; j < size - 1; j++) {
            if (walls[i][j] === "VERTICAL") {
                verticalWalls = Array.from(document.getElementsByClassName(`vertical-wall-${i}-${j}`));
                verticalWalls.forEach(verticalWall => {
                    if (!verticalWall.classList.contains("placed")) {
                        verticalWall.className = verticalWall.className + " placed"
                    }
                });

                corner = document.getElementById(`corner-${i}-${j}`);
                if (!corner.classList.contains("placed")) {
                    corner.className = corner.className + " placed";
                }
            }
            if (walls[i][j] === "HORIZONTAL") {
                horizontalWalls = Array.from(document.getElementsByClassName(`horizontal-wall-${i}-${j}`));
                horizontalWalls.forEach(horizontalWall => {
                    if (!horizontalWall.classList.contains("placed")) {
                        horizontalWall.className = horizontalWall.className + " placed"
                    }
                });

                corner = document.getElementById(`corner-${i}-${j}`);
                if (!corner.classList.contains("placed")) {
                    corner.className = corner.className + " placed";
                }
            }
        }
    }

    for (let i = 0; i < 2; i++) {
        document.getElementById(`game-player-${i + 1}-username`).innerText = usernames[i];
        document.getElementById(`game-player-${i + 1}-number-walls`).innerText = nbWalls[i] + " walls left";
    }

    if (!winnerIsDisplayed && winner != "NONE") {
        displayWinner();
    }
}

function displayWinner() {
    winnerIsDisplayed = true;
    const winnerPage = document.getElementById("winner-page");
    winnerPage.style.animation = "displayWinner 0.8s ease-out forwards";

    const winnerImage = document.getElementById("winner-image");
    winnerImage.src = `../${winner.toLowerCase()}.png`;
    winnerImage.alt = `${winner.toLowerCase()}`;

    const winnerUsername = document.getElementById("winner-username");
    winnerUsername.innerText = (winner === "PLAYER_1" ? usernames[0] : usernames[1]) + " has won the game !";
    if (!(winnerUsername.classList.contains("winner-username-1") || winnerUsername.classList.contains("winner-username-2"))) {

    }
    winnerUsername.className = winnerUsername.className + " winner-username-" + (winner === "PLAYER_1" ? "1" : "2")
}

function disableWinnerPage() {
    const winnerPage = document.getElementById("winner-page");
    winnerPage.style.display = "none";
}

async function refreshAndDisplay() {
    await refresh();
    display();
}

async function main() {
    await refresh();
    generate();
    display();

    setInterval(refreshAndDisplay, 1000);
}

function navigateBack() {
    document.location.href = "../games";
}

function navigateHome() {
    document.location.href = "../";
}

main()