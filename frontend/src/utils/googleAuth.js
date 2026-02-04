// Reusable Google Auth Utility Functions
import { useNotification } from '../components/NotificationProvider';

// Common Google SDK loading function
export const loadGoogleSDK = (buttonId, onSuccess, onError) => {
    // Load Google SDK script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
        if (window.google && window.google.accounts) {
            // Use environment variable instead of hardcoded ID
            const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
            
            if (!clientId || clientId === 'YOUR_GOOGLE_CLIENT_ID_HERE') {
                console.error('Google Client ID not configured');
                if (onError) onError('Google Client ID not configured');
                return;
            }
            
            window.google.accounts.id.initialize({
                client_id: clientId,
                callback: onSuccess,
                auto_select: false,
                itp_support: true,
            });

            const buttonElement = document.getElementById(buttonId);
            if (buttonElement) {
                window.google.accounts.id.renderButton(buttonElement, {
                    type: 'standard',
                    theme: 'outline',
                    size: 'large',
                    text: buttonId.includes('signup') ? 'signup_with' : 'signin_with',
                    locale: 'en'
                });
            }
        } else {
            console.error('Google SDK not loaded');
            if (onError) onError('Failed to load Google SDK');
        }
    };

    script.onerror = (error) => {
        console.error('Failed to load Google SDK script:', error);
        if (onError) onError(error);
    };

    document.head.appendChild(script);
};

// Common Google login initialization function
export const initializeGoogleLogin = (containerId, onSuccessCallback, onErrorCallback, clientIdOverride = null) => {
    if (window.google && window.google.accounts) {
        try {
            // Try both Vite and React App environment variable names
            const viteClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
            const reactClientId = import.meta.env.REACT_APP_GOOGLE_CLIENT_ID;
            const envClientId = viteClientId || reactClientId || undefined;
            
            // Use override if provided, otherwise use environment variable
            const clientId = clientIdOverride || envClientId;

            console.log('VITE_GOOGLE_CLIENT_ID:', viteClientId);
            console.log('REACT_APP_GOOGLE_CLIENT_ID:', reactClientId);
            console.log('Final Client ID:', clientId); // Debug log

            if (!clientId || clientId === 'YOUR_GOOGLE_CLIENT_ID_HERE' || clientId === '') {
                // Show a warning if the client ID is not configured
                const buttonContainer = document.getElementById(containerId);
                if (buttonContainer) {
                    buttonContainer.innerHTML = '';
                    const configButton = document.createElement('button');
                    configButton.className = 'social-btn google-btn';
                    configButton.type = 'button';
                    configButton.innerHTML = '<span>🔵</span> Continue with Google';
                    configButton.onclick = () => {
                        if (onErrorCallback) {
                            onErrorCallback('Google authentication is not configured. Please set up your Google Client ID in the environment variables.');
                        }
                    };
                    buttonContainer.appendChild(configButton);
                }
                console.warn('Google Client ID is not configured properly');
                return;
            }

            // Validate client ID format (should end with '.googleusercontent.com')
            if (!clientId.endsWith('.googleusercontent.com')) {
                console.error('Invalid Google Client ID format. It should end with ".googleusercontent.com"');
                const buttonContainer = document.getElementById(containerId);
                if (buttonContainer) {
                    buttonContainer.innerHTML = '';
                    const errorButton = document.createElement('button');
                    errorButton.className = 'social-btn google-btn';
                    errorButton.type = 'button';
                    errorButton.innerHTML = '<span>🔵</span> Continue with Google';
                    errorButton.onclick = () => {
                        if (onErrorCallback) {
                            onErrorCallback('Invalid Google Client ID format. Please check your configuration.');
                        }
                    };
                    buttonContainer.appendChild(errorButton);
                }
                return;
            }

            window.google.accounts.id.initialize({
                client_id: clientId,
                callback: onSuccessCallback,
            });

            // Check if the button container exists before rendering
            const buttonContainer = document.getElementById(containerId);
            if (buttonContainer) {
                // Clear the container first to ensure no conflicts
                buttonContainer.innerHTML = '';

                window.google.accounts.id.renderButton(buttonContainer, {
                    theme: 'outline',
                    size: 'large',
                    width: '100%',
                    text: containerId.includes('signup') ? 'signup_with' : 'continue_with'
                });

                // Apply custom styling after the button is rendered
                setTimeout(() => {
                    const iframe = buttonContainer.querySelector('iframe');
                    if (iframe) {
                        iframe.style.borderRadius = '8px';
                        iframe.style.border = 'none';
                    }
                }, 100);
            }
        } catch (error) {
            console.error(`Error initializing Google login for ${containerId}:`, error);
            // Show fallback button if initialization fails
            const buttonContainer = document.getElementById(containerId);
            if (buttonContainer) {
                buttonContainer.innerHTML = '';
                const fallbackButton = document.createElement('button');
                fallbackButton.className = 'social-btn google-btn';
                fallbackButton.type = 'button';
                fallbackButton.innerHTML = '<span>🔵</span> Continue with Google';
                fallbackButton.onclick = () => {
                    if (onErrorCallback) {
                        onErrorCallback('Error initializing Google authentication. Please check your browser console for details and ensure your Google Client ID is properly configured.');
                    }
                };
                buttonContainer.appendChild(fallbackButton);
            }
        }
    } else {
        console.error('Google SDK not loaded properly');
    }
};