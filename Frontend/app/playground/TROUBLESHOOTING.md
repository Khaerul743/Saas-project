# Playground Troubleshooting Guide

## Common Issues

### 1. 401 Unauthorized Error

**Problem**: Backend returns 401 Unauthorized when calling `/api/agents/invoke/{agent_id}`

**Error Message**:
```
2025-09-21 20:40:09,841 | WARNING | app.dependencies.auth | Access attempt without token
INFO: 127.0.0.1:62858 - "POST /api/agents/invoke/11 HTTP/1.1" 401 Unauthorized
```

**Root Cause**: Authentication token/cookie not being sent with the request

**Solution**:
1. ✅ **Fixed**: Use `playgroundService.invokeAgent()` instead of direct axios calls
2. ✅ **Fixed**: Updated axios config to use `http://localhost:8080/api` as default
3. ✅ **Fixed**: Using `withCredentials: true` for cookie-based authentication

**Verification**:
- Check browser DevTools → Network tab
- Look for `Cookie` header in the request
- Verify the request goes to correct endpoint

### 2. CORS Issues

**Problem**: CORS errors when calling API from frontend

**Solution**:
- Backend should allow credentials: `Access-Control-Allow-Credentials: true`
- Backend should allow origin: `Access-Control-Allow-Origin: http://localhost:3000`

### 3. Wrong Base URL

**Problem**: API calls going to wrong endpoint

**Current Configuration**:
```typescript
// lib/axios_config.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api'
```

**To Change**:
1. Create `.env.local` file:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api
```

### 4. Authentication Not Working

**Checklist**:
- [ ] User is logged in (check auth context)
- [ ] Cookies are being sent (check DevTools)
- [ ] Backend is running on correct port
- [ ] Using `playgroundService` instead of direct axios

### 5. Agent Not Found

**Problem**: 404 error when calling agent endpoint

**Solution**:
- Verify agent ID exists in database
- Check if agent is active
- Ensure user has access to the agent

## Debug Steps

### 1. Check Browser Console
```javascript
// Look for these logs:
[Axios Config] API_BASE_URL: http://localhost:8080/api
[API Request] POST /agents/invoke/11
[API Response] 200 /agents/invoke/11
```

### 2. Check Network Tab
- Request URL: `http://localhost:8080/api/agents/invoke/11`
- Request Method: `POST`
- Request Headers: Should include `Cookie`
- Request Payload: `{"message":"hai"}`

### 3. Check Backend Logs
- Look for authentication warnings
- Check if token is being validated
- Verify agent exists and is accessible

## Testing Commands

### Test API Directly
```bash
# Test with curl (replace with actual cookie)
curl -X POST http://localhost:8080/api/agents/invoke/11 \
  -H "Content-Type: application/json" \
  -H "Cookie: your-auth-cookie-here" \
  -d '{"message": "hai"}'
```

### Test Authentication
```bash
# Check if user is authenticated
curl -X GET http://localhost:8080/api/users/profile \
  -H "Cookie: your-auth-cookie-here"
```

## Environment Setup

### Frontend (.env.local)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api
```

### Backend
- Ensure CORS is configured for `http://localhost:3000`
- Ensure authentication middleware is working
- Ensure agent endpoint exists and is accessible

## Common Fixes

1. **Clear browser cookies** and login again
2. **Restart both frontend and backend** servers
3. **Check backend logs** for authentication issues
4. **Verify agent ID** exists in database
5. **Test with Postman** to isolate frontend vs backend issues
