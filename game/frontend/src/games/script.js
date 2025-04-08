let team = "NONE";

async function createGame() {
    const size = document.getElementById("board-size-input").value;
    const nbWalls = document.getElementById("number-walls-input").value;
    const turnStart = team;


    const response = await fetch(`${backendURL}/game`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        },
        body: JSON.stringify({ size, nbWalls, turnStart })
    });
    if (response.ok) {
        const json = await response.json();
        const joinedGame = JSON.parse(sessionStorage.getItem("joinedGame")) || [];
        joinedGame.push(json.UUID);
        sessionStorage.setItem("joinedGame", JSON.stringify(joinedGame));
        document.location.href = `../game?uuid=${json.UUID}`;
        return;
    }
    else {
        location.reload();
        return;
    }
}

function navigateBack() {
    document.location.href = "../";
}

function navigateHome() {
    document.location.href = "../";
}

function boardSizeOutput() {
    document.getElementById("board-size-output").innerText = document.getElementById("board-size-input").value;
}

function numberWallsOutput() {
    document.getElementById("number-walls-output").innerText = document.getElementById("number-walls-input").value;
}

function selectTeam(selection) {
    team = selection;
    const teamRandom = document.getElementById("team-random");
    const teamDolphin = document.getElementById("team-dolphin");
    const teamShark = document.getElementById("team-shark");

    if (selection === "NONE") {
        teamRandom.className += " clicked";
        teamDolphin.classList.remove("clicked");
        teamShark.classList.remove("clicked");
    }
    else if (selection === "FIRST") {
        teamRandom.classList.remove("clicked");
        teamDolphin.className += " clicked";
        teamShark.classList.remove("clicked");
    }
    else {
        teamRandom.classList.remove("clicked");
        teamDolphin.classList.remove("clicked");
        teamShark.className += " clicked";
    }
}

function createCell(UUID, x, y, size) {
    const element = document.createElement("div");
    element.className = "cell";
    element.id = `cell-${UUID}-${x}-${y}`;

    return element;
}

function createHorizontalWall(UUID, x, y, size) {
    const element = document.createElement("div");
    element.className = "horizontal-wall";
    if (y != 0) element.className = element.className + ` horizontal-wall-${UUID}-${x}-${y - 1}`;
    if (y != size - 1) element.className = element.className + ` horizontal-wall-${UUID}-${x}-${y}`;

    return element;
}

function createVerticalWall(UUID, x, y, size) {
    const element = document.createElement("div");
    element.className = "vertical-wall";
    if (x != 0) element.className = element.className + ` vertical-wall-${UUID}-${x - 1}-${y}`;
    if (x != size - 1) element.className = element.className + ` vertical-wall-${UUID}-${x}-${y}`;
    
    return element;
}

function createCorner(UUID, x, y, size) {
    const element = document.createElement("div");
    element.className = "corner";
    element.id = `corner-${UUID}-${x}-${y}`

    return element;
}

createElement = [createCell, createVerticalWall, createHorizontalWall, createCorner];

function createInformation(UUID) {
    const gameInformation = document.createElement("div");
    gameInformation.className = "game-information";
    gameInformation.id = `game-information-${UUID}`;

    for (let i = 0; i < 2; i++) {
        const player = document.createElement("div");
        player.className = `game-player-${i + 1}`;

        const playerImage = document.createElement("img");
        playerImage.src = `../player_${i + 1}.png`;
        playerImage.alt = `player_${i + 1}`;

        const playerUsername = document.createElement("div");
        playerUsername.className = `game-player-${i + 1}-username`;
        playerUsername.id = `game-player-${i + 1}-username-${UUID}`

        player.appendChild(playerImage);
        player.appendChild(playerUsername);

        gameInformation.appendChild(player);
    }

    const status = document.createElement("div");
    status.className = "game-status";
    status.id = `game-status-${UUID}`;

    gameInformation.appendChild(status);

    const buttons = document.createElement("div");
    buttons.className = "game-buttons";

    const joinButton = document.createElement("button");
    joinButton.className = "game-join-button";
    joinButton.id = `game-join-button-${UUID}`
    joinButton.addEventListener("click", () => join(UUID));
    joinButton.innerText = "Join";

    const spectateButton = document.createElement("button");
    spectateButton.className = "game-spectate-button";
    spectateButton.id = `game-spectate-button-${UUID}`
    spectateButton.addEventListener("click", () => spectate(UUID));
    spectateButton.innerText = "Spectate";

    buttons.appendChild(joinButton);
    buttons.appendChild(spectateButton);

    gameInformation.appendChild(buttons);

    return gameInformation;
}

function generate(game) {
    const gameWrap = document.createElement("div");
    gameWrap.className = "game";
    const gameBoard = document.createElement("div");
    gameBoard.className = "game-board";
    gameBoard.id = `game-board-${game.UUID}`;

    gameBoard.style.gridTemplateColumns = `repeat(${game.board.size * 2 - 1}, auto)`;
    gameBoard.style.gridTemplateRows = `repeat(${game.board.size * 2 - 1}, auto)`;

    for (let i = 0; i < game.board.size * 2 - 1; i++) {
        for (let j = 0; j < game.board.size * 2 - 1; j++) {
            gameBoard.appendChild(createElement[i % 2 * 2 + j % 2](game.UUID, Math.floor(i / 2), Math.floor(j / 2), game.board.size));
        }
    }

    gameWrap.appendChild(gameBoard);
    gameWrap.appendChild(createInformation(game.UUID))

    const games = document.getElementById("join-page");
    games.appendChild(gameWrap);

    game.board.positions.forEach((pos, index) => {
        const cell = document.getElementById(`cell-${game.UUID}-${pos.x}-${pos.y}`);
        const player = document.createElement("div");
        player.className = `player`;
        player.id = `player-${index + 1}-${game.UUID}`;
        cell.appendChild(player);

        const image = document.createElement("img");
        image.src = `../player_${index + 1}.png`;
        image.alt = `player_1`;
        player.appendChild(image);
    });
}

async function getGames() {
    const response = await fetch(`${backendURL}/games`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        }
    });
    if (!response.ok) {
        document.location.href = "../";
        return;
    }

    return await response.json();
}

function generates(games) {
    for (let game of games) {
        generate(game);
    }

    select(window.location.hash.substring(1));

    boardSizeOutput();
    document.getElementById("board-size-input").addEventListener("input", () => {
        boardSizeOutput();
    })

    numberWallsOutput();
    document.getElementById("number-walls-input").addEventListener("input", () => {
        numberWallsOutput();
    })
    
}

function spectate(UUID) {
    document.location.href = `../game?uuid=${UUID}`;
}

function select(Tab) {
    const menuCreate = document.getElementById("menu-create");
    const createPage = document.getElementById("create-page");

    const menuJoin = document.getElementById("menu-join");
    const joinPage = document.getElementById("join-page");

    if (Tab.toLowerCase() === "create") {
        if (!menuCreate.classList.contains("selected")) {
            menuCreate.className += " selected";
            createPage.classList.remove("disable");

            menuJoin.classList.remove("selected");
            joinPage.className += " disable";
        }
    }
    else {
        if (!menuJoin.classList.contains("selected")) {
            menuCreate.classList.remove("selected");
            createPage.className += " disable";

            menuJoin.className += " selected";
            joinPage.classList.remove("disable");
        }
    }
}

async function join(UUID) {
    const joinedGame = JSON.parse(sessionStorage.getItem("joinedGame")) || [];
    if (joinedGame.includes(UUID))
    {
        document.location.href = `../game?uuid=${UUID}`;
        return;
    }
    joinedGame.push(UUID);
    sessionStorage.setItem("joinedGame", JSON.stringify(joinedGame));
    const response = await fetch(`${backendURL}/game/${UUID}/join`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        }
    });
    if (!response.ok) {
        location.reload();
        return;
    }
    else {
        document.location.href = `../game?uuid=${UUID}`;
        return;
    }
}

function display(games) {
    for (game of games) {
        if (document.getElementById(`game-board-${game.UUID}`) === null) {
            generate(game);
        }
        game.board.positions.forEach((position, index) => {
            const cell = document.getElementById(`cell-${game.UUID}-${position.x}-${position.y}`);
            cell.appendChild(document.getElementById(`player-${index + 1}-${game.UUID}`));
        });

        Array.from(document.getElementsByClassName(`placed-${game.UUID}`)).forEach(wall => { wall.classList.remove(`placed-${game.UUID}`);  wall.classList.remove(`placed`);});

        for (i = 0; i < game.board.size - 1; i++) {
            for (j = 0; j < game.board.size - 1; j++) {
                if (game.board.walls[i][j] === "VERTICAL") {
                    verticalWalls = Array.from(document.getElementsByClassName(`vertical-wall-${game.UUID}-${i}-${j}`));
                    verticalWalls.forEach(verticalWall => {
                        if (!verticalWall.classList.contains(`placed-${game.UUID}`)) {
                            verticalWall.className = verticalWall.className + ` placed-${game.UUID} ` + ` placed`
                        }
                    });

                    corner = document.getElementById(`corner-${game.UUID}-${i}-${j}`);
                    if (!corner.classList.contains(`placed-${game.UUID}`)) {
                        corner.className = corner.className + ` placed-${game.UUID}` + ` placed`;
                    }
                }
                if (game.board.walls[i][j] === "HORIZONTAL") {
                    horizontalWalls = Array.from(document.getElementsByClassName(`horizontal-wall-${game.UUID}-${i}-${j}`));
                    horizontalWalls.forEach(horizontalWall => {
                        if (!horizontalWall.classList.contains(`placed-${game.UUID}`)) {
                            horizontalWall.className = horizontalWall.className + ` placed-${game.UUID}` + ` placed`
                        }
                    });

                    corner = document.getElementById(`corner-${game.UUID}-${i}-${j}`);
                    if (!corner.classList.contains(`placed-${game.UUID}`)) {
                        corner.className = corner.className + ` placed-${game.UUID}` + ` placed`;
                    }
                }
            }
        }

        for (let i = 0; i < 2; i++) {
            document.getElementById(`game-player-${i + 1}-username-${game.UUID}`).innerText = game.usernames[i];
        }

        const status = document.getElementById(`game-status-${game.UUID}`);

        if ((JSON.parse(sessionStorage.getItem("joinedGame")) || []).includes(game.UUID)) {
            document.getElementById(`game-spectate-button-${game.UUID}`).style.display = "none";
        }
        if (game.usernames[0] === null || game.usernames[1] === null) {
            status.innerText = "Waiting...";
            document.getElementById(`game-information-${game.UUID}`).className += " permanant";
        }
        else {
            if (!(JSON.parse(sessionStorage.getItem("joinedGame")) || []).includes(game.UUID)) {
                document.getElementById(`game-join-button-${game.UUID}`).style.display = "none";
            }
            if (game.winner != "NONE") {
                status.innerText = "Game over !";
                document.getElementById(`game-information-${game.UUID}`).className += " permanant";
            }
            else {
                status.innerText = "Running...";
                document.getElementById(`game-information-${game.UUID}`).classList.remove("permanant");
            }
        }
    }
}

async function getAndDisplay() {
    display(await getGames());
}

async function main() {
    const json = await getGames();
    generates(json);
    display(json);

    setInterval(getAndDisplay, 1000);
}

main()