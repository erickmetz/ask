async function authenticate() {
    const apiKey = document.getElementById('api-key').value;
    try {
        // Clear any existing credentials
        document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
        localStorage.removeItem('user');
        
        const response = await fetch('/api/v1/demo/token', {
            method: 'POST',
            headers: {
                'X-API-Key': apiKey
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            // Store both token and user info
            const oneHourFromNow = new Date();
            oneHourFromNow.setHours(oneHourFromNow.getHours() + 1);
            document.cookie = `token=${data.access_token}; SameSite=Strict; expires=${oneHourFromNow.toUTCString()}; path=/`;
            localStorage.setItem('user', data.user);
            showAuthenticatedState(data.user);
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Authentication failed');
        }
    } catch (error) {
        alert(error.message || 'Authentication failed. Please check your API key.');
    }
}

function getToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'token') {
            return value;
        }
    }
    return null;
}

function showAuthenticatedState(user) {
    document.getElementById('auth-form').style.display = 'none';
    document.getElementById('api-section').style.display = 'block';
    document.getElementById('welcome').textContent = `Welcome to the ASK-API demo, ${user}!`;
}

async function makeRequest() {
    try {
        const token = getToken();
        if (!token) {
            throw new Error('No authentication token found');
        }

        const response = await fetch('/api/v1/secure/ask', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.style.color = '#ffffff';  // Reset to default white color
            resultDiv.textContent = `Question: ${data.question}`;
        } else if (response.status === 429) {
            const errorData = await response.json();
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.style.color = '#ff6b6b';  // Red color for rate limit errors
            resultDiv.textContent = errorData.detail || 'Rate limit exceeded. Please wait before making more requests.';
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Request failed');
        }
    } catch (error) {
        alert('Failed to make request. Please try authenticating again.');
        showUnauthenticatedState();
    }
}

function showUnauthenticatedState() {
    document.getElementById('auth-form').style.display = 'block';
    document.getElementById('api-section').style.display = 'none';
    document.getElementById('welcome').textContent = 'Welcome to the Ask API demo!';
    localStorage.removeItem('user');
    // Clear the token cookie
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
}

// Check for existing token on page load
window.onload = async function() {
    const token = getToken();
    if (token) {
        try {
            // Validate the token by making a request
            const response = await fetch('/api/v1/secure/ask', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const user = localStorage.getItem('user');
                if (user) {
                    showAuthenticatedState(user);
                } else {
                    showAuthenticatedState('User');
                }
            } else {
                showUnauthenticatedState();
            }
        } catch (error) {
            showUnauthenticatedState();
        }
    }
}; 