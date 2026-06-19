// Reusable Google Auth Utility Functions

// Common Google SDK loading function
export const loadGoogleSDK = (buttonId, onSuccess, onError) => {
    if (import.meta.env.DEV) console.log('🔵 [GoogleAuth] Loading Google SDK for button:', buttonId);

    const SDK_URL = 'https://accounts.google.com/gsi/client';

    // Bug #34 fixed: check if the script tag already exists to prevent duplicates.
    // Multiple components (Login, Register) each called loadGoogleSDK on mount,
    // causing N script tags and N SDK initialisations for N components.
    const existing = document.querySelector(`script[src="${SDK_URL}"]`);
    if (existing) {
        // Script already in DOM: if SDK is already loaded, initialise immediately;
        // otherwise, piggyback on the existing script's load event.
        if (window.google && window.google.accounts) {
            initGoogleButton(buttonId, onSuccess, onError);
        } else {
            existing.addEventListener('load', () => initGoogleButton(buttonId, onSuccess, onError));
        }
        return;
    }

    // Load Google SDK script
    const script = document.createElement('script');
    script.src = SDK_URL;
    script.async = true;
    script.defer = true;

    script.onload = () => {
        if (import.meta.env.DEV) console.log('✅ [GoogleAuth] Google SDK script loaded');
        initGoogleButton(buttonId, onSuccess, onError);
    };

    script.onerror = () => {
        const errorMsg = 'Failed to load Google SDK script';
        console.error('❌ [GoogleAuth]', errorMsg);
        if (onError) onError(errorMsg);
    };

    document.head.appendChild(script);
};

const clearElementChildren = (element) => {
    if (!element) return;
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
};

// Bug #34 fix: extracted SDK-dependent initialisation into its own function
// so it can be called both from a fresh script load and from the dedup path.
const initGoogleButton = (buttonId, onSuccess, onError) => {
        
        if (window.google && window.google.accounts) {
            // Use environment variable instead of hardcoded ID
            const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
            
            if (import.meta.env.DEV) console.log('🔑 [GoogleAuth] VITE_GOOGLE_CLIENT_ID:', clientId ? 'CONFIGURED' : 'NOT CONFIGURED');

            if (!clientId || clientId === 'YOUR_GOOGLE_CLIENT_ID_HERE' || clientId === '') {
                const errorMsg = 'Google Client ID not configured. Please set VITE_GOOGLE_CLIENT_ID in .env file';
                console.error('❌ [GoogleAuth]', errorMsg);
                console.error('📝 [GoogleAuth] Get your Client ID from: https://console.cloud.google.com/apis/credentials');
                
                // Show visible error in the button container
                const buttonElement = document.getElementById(buttonId);
                if (buttonElement) {
                    buttonElement.textContent = '';
                    const wrapper = document.createElement('div');
                    wrapper.style.cssText = 'background:#fef2f2;border:1px solid #ef4444;border-radius:8px;padding:16px;text-align:center;';
                    const title = document.createElement('span');
                    title.style.cssText = 'color:#dc2626;font-weight:600;font-size:14px;';
                    title.textContent = '⚠️ Google Login Not Configured';
                    const desc = document.createElement('p');
                    desc.style.cssText = 'color:#991b1b;font-size:12px;margin:8px 0 0 0;';
                    desc.textContent = 'Set VITE_GOOGLE_CLIENT_ID in .env file ';
                    const link = document.createElement('a');
                    link.href = 'https://console.cloud.google.com/apis/credentials';
                    link.target = '_blank';
                    link.style.cssText = 'color:#2563eb;text-decoration:underline;';
                    link.textContent = 'Get Client ID here';
                    desc.appendChild(link);
                    wrapper.appendChild(title);
                    wrapper.appendChild(desc);
                    buttonElement.appendChild(wrapper);
                }
                
                if (onError) onError(errorMsg);
                return;
            }

            if (import.meta.env.DEV) console.log('✅ [GoogleAuth] Initializing Google OAuth');
            
            window.google.accounts.id.initialize({
                client_id: clientId,
                callback: onSuccess,
                auto_select: false,
                itp_support: true,
            });

            const buttonElement = document.getElementById(buttonId);
            if (buttonElement) {
                if (import.meta.env.DEV) console.log('🔘 [GoogleAuth] Rendering Google button:', buttonId);
                window.google.accounts.id.renderButton(buttonElement, {
                    type: 'standard',
                    theme: 'outline',
                    size: 'large',
                    text: buttonId.includes('signup') ? 'signup_with' : 'signin_with',
                    locale: 'en'
                });
            } else {
                console.error('❌ [GoogleAuth] Button container not found:', buttonId);
            }
        } else {
            console.error('❌ [GoogleAuth] Google SDK not loaded properly');
            if (onError) onError('Failed to load Google SDK');
        }
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

            if (import.meta.env.DEV) {
                console.log('VITE_GOOGLE_CLIENT_ID:', viteClientId);
                console.log('REACT_APP_GOOGLE_CLIENT_ID:', reactClientId);
                console.log('Final Client ID:', clientId);
            }

            if (!clientId || clientId === 'YOUR_GOOGLE_CLIENT_ID_HERE' || clientId === '') {
                // Show a warning if the client ID is not configured
                const buttonContainer = document.getElementById(containerId);
                if (buttonContainer) {
                    clearElementChildren(buttonContainer);
                    const configButton = document.createElement('button');
                    configButton.className = 'social-btn google-btn';
                    configButton.type = 'button';
                    configButton.textContent = '🔵 Continue with Google';
                    configButton.onclick = () => {
                        if (onErrorCallback) {
                            onErrorCallback('Google authentication is not configured. Please set up your Google Client ID in the environment variables.');
                        }
                    };
                    buttonContainer.appendChild(configButton);
                }
                if (import.meta.env.DEV) console.warn('Google Client ID is not configured properly');
                return;
            }

            // Validate client ID format (should end with '.googleusercontent.com')
            if (!clientId.endsWith('.googleusercontent.com')) {
                console.error('Invalid Google Client ID format. It should end with ".googleusercontent.com"');
                const buttonContainer = document.getElementById(containerId);
                if (buttonContainer) {
                    clearElementChildren(buttonContainer);
                    const errorButton = document.createElement('button');
                    errorButton.className = 'social-btn google-btn';
                    errorButton.type = 'button';
                    errorButton.textContent = '🔵 Continue with Google';
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
                clearElementChildren(buttonContainer);

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
                clearElementChildren(buttonContainer);
                const fallbackButton = document.createElement('button');
                fallbackButton.className = 'social-btn google-btn';
                fallbackButton.type = 'button';
                fallbackButton.textContent = '🔵 Continue with Google';
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