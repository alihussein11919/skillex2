document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("signupForm").addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent the form from reloading the page

        // Get form values
        const firstName = document.getElementById("first_name").value;
        const lastName = document.getElementById("last_name").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const role = document.getElementById("role").value;

        // Prepare data for API
        const userData = {
            first_name: firstName,
            last_name: lastName,
            email: email,
            password: password,
            role: role
        };

        try {
            // Send data to the backend
            const response = await fetch("/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(userData)
            });

            const result = await response.json();
            
            if (response.ok) {
                alert("Signup successful! Redirecting...");
                window.location.href = "/login"; // Redirect to login page
            } else {
                alert("Signup failed: " + result.error);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        }
    });
});
