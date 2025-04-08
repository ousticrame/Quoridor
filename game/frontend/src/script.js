async function createUser() {
    const username = document.getElementById("home-username").value;
    const response = await fetch(`${backendURL}/user`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username })
    });
    if (response.ok) {
        const json = await response.json();
        sessionStorage.clear();
        sessionStorage.setItem("playerID", json.UUID);
        document.location.href = "games";
        return;
    } else {
        document.getElementById("invalid-username").style.transition = "none";
        document.getElementById("invalid-username").style.opacity = 1;
        setTimeout(() => {
            document.getElementById("invalid-username").style.transition = "opacity 1s ease";
            document.getElementById("invalid-username").style.opacity = 0
        }, 3000)
    }
}