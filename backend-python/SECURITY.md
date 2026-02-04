# Security Best Practices

## Environment Variables

### JWT Secret
- **CRITICAL**: Never use default or placeholder JWT secrets in production
- Generate a strong, random secret using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Store the secret in environment variables, never in code
- Example: `JWT_SECRET=your_very_long_random_secret_here`

## API Security

### Token Verification
- All protected endpoints require valid JWT tokens
- Tokens are validated against the configured JWT secret
- Expired or invalid tokens return 401 Unauthorized status

### Data Access
- All database operations are authenticated
- User data is isolated by user ID
- No cross-user data access is permitted

## Production Deployment

### Environment Configuration
- Ensure JWT_SECRET is properly set before deployment
- The application will log security warnings if critical secrets are missing
- Monitor application logs for security warnings

### Model Security
- ML models are loaded from secure local storage
- Model files should have appropriate file permissions
- Protect model files from unauthorized access