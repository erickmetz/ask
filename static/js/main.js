function showModal(message) {
    const modalOverlay = document.getElementById('modal-overlay');
    const modalBox = document.getElementById('modal-box');
    modalBox.textContent = message;
    modalOverlay.classList.remove('hidden');
    modalOverlay.classList.add('modal-overlay', 'show');
    setTimeout(() => {
        modalOverlay.classList.remove('show');
        modalOverlay.classList.add('hidden');
    }, 1000);
}

async function fetchAuthorizedChannels() {
    try {
        const token = getToken();
        if (!token) {
            throw new Error('No authentication token found');
        }

        const response = await fetch('/api/v1/demo/channels', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const channelSelect = document.getElementById('channel-select');
            
            // Clear existing options
            while (channelSelect.options.length > 0) {
                channelSelect.remove(0);
            }
            
            // Add authorized channels
            data.channels.forEach(channel => {
                const option = document.createElement('option');
                option.value = channel;
                option.textContent = channel.charAt(0).toUpperCase() + channel.slice(1);
                channelSelect.appendChild(option);
            });
        } else {
            throw new Error('Failed to fetch authorized channels');
        }
    } catch (error) {
        console.error('Error fetching channels:', error);
        showModal('Failed to load available channels');
    }
}

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
            await fetchAuthorizedChannels();  // Fetch channels after successful authentication
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Authentication failed');
        }
    } catch (error) {
        showModal(error.message || 'Authentication failed. Please check your API key.');
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
    document.getElementById('auth-form').classList.add('hidden');
    document.getElementById('api-section').classList.remove('hidden');
    document.getElementById('welcome').textContent = `Welcome to the ASK-API demo, ${user}!`;
    document.getElementById('result').classList.add('hidden');
}

async function makeRequest() {
    try {
        const token = getToken();
        if (!token) {
            throw new Error('No authentication token found');
        }

        const channelSelect = document.getElementById('channel-select');
        let channel = null;
        
        if (channelSelect) {
            const selectedOptions = Array.from(channelSelect.selectedOptions);
            if (selectedOptions.length > 0) {
                // Only include non-empty values in the channel list
                channel = selectedOptions
                    .map(option => option.value)
                    .filter(value => value !== '')
                    .join(',');
            }
        }
        
        const url = new URL('/api/v1/secure/ask', window.location.origin);
        if (channel) {
            url.searchParams.append('channel', channel);
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden', 'result-error');
            resultDiv.classList.add('show', 'result-ok');
            resultDiv.textContent = `Question: ${data.question}`;
        } else if (response.status === 429 || response.status === 400) {
            const errorData = await response.json();
            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden', 'result-ok');
            resultDiv.classList.add('show', 'result-error');
            resultDiv.textContent = errorData.detail || (response.status === 429 ? 'Rate limit exceeded. Please wait before making more requests.' : 'Invalid request. Please check your channel selection.');
        } else if (response.status === 403) {
            const errorData = await response.json();
            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden', 'result-ok');
            resultDiv.classList.add('show', 'result-error');
            resultDiv.textContent = errorData.detail || 'Access denied. Please check your channel authorization.';
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Request failed');
        }
    } catch (error) {
        showModal('Failed to make request. Please try authenticating again.');
        showUnauthenticatedState();
    }
}

function showUnauthenticatedState() {
    document.getElementById('auth-form').classList.remove('hidden');
    document.getElementById('api-section').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('welcome').textContent = 'Welcome to the Ask API demo!';
    localStorage.removeItem('user');
    // Clear the token cookie
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
}

// Add event listener to the authenticate button
document.getElementById('authenticate-btn').addEventListener('click', authenticate);

// Add event listener to the make request button
document.getElementById('make-request-btn').addEventListener('click', makeRequest);

// Add event listener to the logout button
document.getElementById('logout-btn').addEventListener('click', showUnauthenticatedState);

// Add event listeners for channel selection
document.getElementById('channel-select').addEventListener('mousedown', function(e) {
    // Prevent default to handle selection ourselves
    e.preventDefault();
    
    const select = this;  // Use 'this' instead of e.target to get the select element
    const option = e.target.closest('option');
    if (!option) return;

    const selectedOptions = Array.from(select.selectedOptions);
    const hasRandom = selectedOptions.some(opt => opt.value === 'random');
    const hasOtherOptions = selectedOptions.some(opt => opt.value !== 'random' && opt.value !== '');
    const isRandom = option.value === 'random';
    const isOther = option.value !== 'random' && option.value !== '';

    // Handle mutual exclusivity
    if (isRandom && hasOtherOptions) {
        // If clicking Random while other options are selected, clear others
        Array.from(select.options).forEach(opt => {
            if (opt.value !== 'random') {
                opt.selected = false;
            }
        });
    } else if (isOther && hasRandom) {
        // If clicking other option while Random is selected, clear Random
        Array.from(select.options).forEach(opt => {
            if (opt.value === 'random') {
                opt.selected = false;
            }
        });
    }

    // Toggle the clicked option
    option.selected = !option.selected;
});

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
                    await fetchAuthorizedChannels();  // Fetch channels after restoring authentication
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