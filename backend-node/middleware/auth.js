const jwt = require('jsonwebtoken');

module.exports = function(req, res, next) {
    const token = req.header('x-auth-token');
    
    console.log('🔐 Auth Middleware - Token received:', token ? 'YES' : 'NO');
    
    if (!token) {
        console.log('❌ No token provided');
        return res.status(401).json({ message: 'No token, authorization denied' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded.user || decoded;
        console.log('✅ Token valid - User ID:', req.user.id);
        next();
    } catch (err) {
        console.log('❌ Token invalid:', err.message);
        // Return 401 for invalid token (not 403)
        res.status(401).json({ message: 'Token is not valid' });
    }
};