# Debug Response Issues

## Problem: Frontend Shows Error Despite Backend Success

### Symptoms
- Backend logs show successful response
- Frontend displays: "Sorry, I encountered an error. Please try again."
- No network errors in browser DevTools

### Root Cause
Response structure mismatch between backend and frontend expectations.

### Backend Response Format
```json
{
  "status": "success",
  "message": "Invoke agent is successfully",
  "data": {
    "user_message": "hai",
    "response": "Halo! Selamat datang! Bagaimana kabarmu hari ini? Apakah ada yang bisa saya bantu? 😊"
  }
}
```

### Frontend Processing
1. `playgroundService.invokeAgent()` calls backend
2. `BaseApiService` unwraps response: `return response.data`
3. Frontend receives unwrapped response
4. Frontend checks `response.status` (not `response.data.status`)

### Debug Steps

#### 1. Check Browser Console
Look for these logs:
```
Sending message to agent: 11 hai
Received response: {status: "success", message: "...", data: {...}}
Success response, data: {user_message: "hai", response: "..."}
```

#### 2. Check Network Tab
- Request: `POST /api/agents/invoke/11`
- Response: Should show the JSON response above
- Status: Should be 200

#### 3. Check Response Structure
```javascript
// In browser console, check:
console.log('Response:', response)
console.log('Response status:', response.status)
console.log('Response data:', response.data)
console.log('Response data.response:', response.data.response)
```

### Common Issues

#### Issue 1: Wrong Response Path
```typescript
// WRONG (old code):
if (response.data.status === 'success') {
  onSendMessage(message, response.data.data.response)
}

// CORRECT (fixed code):
if (response.status === 'success') {
  onSendMessage(message, response.data.response)
}
```

#### Issue 2: Response Not Unwrapped
If using direct axios instead of BaseApiService:
```typescript
// Direct axios response:
response.data.status === 'success'
response.data.data.response

// BaseApiService response (unwrapped):
response.status === 'success'
response.data.response
```

### Testing Commands

#### Test Response Structure
```javascript
// In browser console:
const testResponse = {
  status: "success",
  message: "Invoke agent is successfully",
  data: {
    user_message: "hai",
    response: "Test response"
  }
}

console.log('Status:', testResponse.status)
console.log('Response:', testResponse.data.response)
```

### Fix Applied
Updated `components/playground/chat-interface.tsx`:
- Changed `response.data.status` to `response.status`
- Changed `response.data.data.response` to `response.data.response`
- Added debug logging for troubleshooting

### Verification
After fix, you should see:
1. Console logs showing successful response
2. Agent response displayed in chat
3. No error messages
