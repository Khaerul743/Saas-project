# Playground API Integration

## Overview
Playground chat interface sekarang terintegrasi dengan backend API untuk mendapatkan response yang real dari AI agents.

## API Endpoint
```
POST http://localhost:8080/api/agents/invoke/{agent_id}
```

### Request Format
```json
{
  "message": "hai"
}
```

### Response Format
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

## Implementation Details

### ChatInterface Component
- **File**: `components/playground/chat-interface.tsx`
- **Changes**:
  - Added `agentId` prop
  - Updated `onSendMessage` to accept both user message and agent response
  - Integrated axios for API calls
  - Real-time API integration with error handling

### API Call Implementation
```typescript
// Using playground service with proper authentication
const response = await playgroundService.invokeAgent(agentId, message)

// This internally calls:
// POST http://localhost:8080/api/agents/invoke/{agentId}
// With payload: { "message": "hai" }
// With authentication headers and cookies

// Response structure (after BaseApiService unwrapping):
// response = {
//   status: "success",
//   message: "Invoke agent is successfully", 
//   data: {
//     user_message: "hai",
//     response: "Halo! Selamat datang!..."
//   }
// }
```

### Playground Page
- **File**: `app/playground/page.tsx`
- **Changes**:
  - Updated `handleSendMessage` to work with new API flow
  - Added proper type handling for Agent interface
  - Integrated with real agent data

### Test Page
- **File**: `app/playground/test/[agentId]/page.tsx`
- **Changes**:
  - Updated to use real API responses
  - Proper error handling for agent loading
  - Type-safe agent data handling

## Type Safety
- Created playground-specific `Agent` type with required `id`
- Proper type conversion from API `Agent` to playground `Agent`
- Type-safe API calls and responses

## Authentication
- Uses `playgroundService` which extends `BaseApiService`
- Automatically includes authentication cookies via `withCredentials: true`
- Uses configured `apiClient` with proper headers and interceptors
- Handles 401 errors with automatic redirect to login

## Error Handling
- API call failures fallback to error messages
- Loading states during API calls
- Proper error display in chat interface
- 401 Unauthorized handling with user feedback

## Usage Flow
1. User types message in chat interface
2. Message sent to backend API endpoint
3. Backend processes with AI agent
4. Response returned and displayed in chat
5. Error handling for failed requests

## Future Enhancements
- Add retry mechanism for failed requests
- Implement streaming responses
- Add typing indicators
- Cache responses for better UX
- Add conversation history persistence
