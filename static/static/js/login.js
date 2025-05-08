document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const userData = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });

    const data = await response.json();

    if (response.ok) {
        alert("Login successful!");
        window.location.href = "/dashboard";  // Redirect to dashboard (to be created later)
    } else {
        alert("Error: " + data.error);
    }
});
