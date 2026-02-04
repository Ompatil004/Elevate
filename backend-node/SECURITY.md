# Security Best Practices

## Environment Variables

### JWT Secret
- **CRITICAL**: Never use default or placeholder JWT secrets in production
- Generate a strong, random secret using: `openssl rand -base64 32`
- Store the secret in environment variables, never in code
- Example: `JWT_SECRET=your_very_long_random_secret_here`

### Google OAuth Credentials
- Keep `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` secure
- Do not share these credentials publicly
- Regularly rotate credentials if compromised
- Use different credentials for development and production

## Authentication Security

### Token Validation
- All API endpoints require valid JWT tokens
- Tokens expire after 7 days to limit exposure
- Invalid tokens return 401 Unauthorized status

### Password Security
- All passwords are hashed using bcrypt with salt rounds
- Plain text passwords are never stored
- Google OAuth users have randomly generated backup passwords

## Production Deployment

### Environment Configuration
- Ensure all environment variables are properly set before deployment
- The application will refuse to start if critical secrets are missing
- Monitor application logs for security warnings

### File Permissions
- Protect model files and sensitive data with appropriate file permissions
- Restrict access to configuration files
- Use secure file storage for production environments