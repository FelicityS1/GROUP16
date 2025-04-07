document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded - initializing login script");

    const loginForm = document.getElementById("loginForm");
    const googleBtn = document.getElementById("googleSignIn");
    
    if (!loginForm) {
        console.error("Login form not found!");
        return;
    }
    
    console.log("Login form found - adding event listener");

    // Display error messages to the user
    function showError(message) {
        const loginResponse = document.getElementById("loginResponse");
        if (loginResponse) {
            loginResponse.textContent = message;
            loginResponse.style.color = "#d32f2f";
            loginResponse.style.backgroundColor = "#ffebee";
            loginResponse.style.padding = "8px";
            loginResponse.style.borderRadius = "4px";
            loginResponse.style.display = "block";
        } else {
            console.error(message);
            alert(message);
        }
    }

    // Display success messages to the user
    function showSuccess(message) {
        const loginResponse = document.getElementById("loginResponse");
        if (loginResponse) {
            loginResponse.textContent = message;
            loginResponse.style.color = "green";
            loginResponse.style.backgroundColor = "#e8f5e9";
            loginResponse.style.padding = "8px";
            loginResponse.style.borderRadius = "4px";
            loginResponse.style.display = "block";
        } else {
            console.log(message);
            alert(message);
        }
    }

    // Handle Google Sign-In click
    if (googleBtn) {
        googleBtn.addEventListener("click", function() {
            window.location.href = "/accounts/google/login/";
        });
    }

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission
        console.log("Login form submitted");

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        
        // Basic validation
        if (!username || !password) {
            showError("Username and password are required");
            return;
        }
        
        console.log(`Attempting login for user: ${username}`);

        try {
            // Get CSRF token
            let csrfToken = getCookie('csrftoken');
            console.log("CSRF token from cookie:", csrfToken ? "Found" : "Not found");

            // If no token in cookie, try to get it from any hidden field
            if (!csrfToken) {
                const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
                if (csrfInput) {
                    csrfToken = csrfInput.value;
                    console.log("CSRF token from input field:", "Found");
                }
            }

            console.log("Trying login endpoint with application/json");
            const response = await fetch("/login_user/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken || ""
                },
                credentials: "include",
                body: JSON.stringify({ 
                    username, 
                    password,
                    role: userRole // Sends selected role to backend
                })
            });
            
            console.log("Login response status:", response.status);
            
            try {
                const data = await response.json();
                console.log("Login response data:", data);
                
                if (data.success === true) {
                    console.log("Login successful! Redirecting to newsfeed");
                    showSuccess("Login successful! Redirecting...");
                    setTimeout(() => {
                        window.location.href = data.redirect || "/newsfeed/";
                    }, 1000);
                } else if (data.error) {
                    showError(`Login failed: ${data.error}`);
                } else {
                    showError("Login failed for an unknown reason.");
                }
            } catch (jsonError) {
                console.error("Error parsing JSON:", jsonError);
                
                // Handle non-JSON responses or redirects
                if (response.redirected) {
                    window.location.href = response.url;
                } else if (response.ok) {
                    showSuccess("Login successful!");
                    setTimeout(() => {
                        window.location.href = "/newsfeed/";
                    }, 1000);
                } else {
                    showError("Login failed. Please check your credentials.");
                }
            }
        } catch (error) {
            console.error("Login error:", error);
            showError("Error connecting to server. Please check if the server is running.");
        }
    });
    
    // Utility function to get cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Additional debugging info
    console.log("Current page URL:", window.location.href);
    console.log("CSRF token cookie:", getCookie('csrftoken') ? "Present" : "Missing");
    console.log("Login script initialization complete");
});