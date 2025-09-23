# Playground Testing Guide

## Testing API Integration

### 1. Backend Setup
Pastikan backend server berjalan di `http://localhost:8080`

### 2. Test API Endpoint
```bash
curl -X POST http://localhost:8080/api/agents/invoke/1 \
  -H "Content-Type: application/json" \
  -d '{"message": "hai"}'
```

Expected Response:
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

### 3. Frontend Testing

#### Test Playground Page
1. Buka `http://localhost:3000/playground`
2. Pilih agent dari sidebar
3. Ketik message: "hai"
4. Tekan Enter atau klik Send
5. Verifikasi response muncul di chat

#### Test Share Link
1. Klik "Share" button
2. Copy share link
3. Buka link di browser baru
4. Test chat functionality

### 4. Error Scenarios

#### Backend Not Running
- Should show error message: "Sorry, I encountered an error. Please try again."

#### Invalid Agent ID
- Should show error message: "Agent not found"

#### Network Error
- Should show error message: "Sorry, I encountered an error. Please try again."

### 5. Expected Behavior

#### Successful Flow
1. User types message
2. Message appears in chat immediately
3. Loading indicator shows
4. API call made to backend
5. Response received and displayed
6. Loading indicator disappears

#### Error Flow
1. User types message
2. Message appears in chat immediately
3. Loading indicator shows
4. API call fails
5. Error message displayed
6. Loading indicator disappears

### 6. Debug Information

Check browser console for:
- API request/response logs
- Error messages
- Network requests in DevTools

### 7. Performance Testing

- Test with multiple rapid messages
- Test with long messages
- Test with special characters
- Test with emojis

### 8. Browser Compatibility

Test on:
- Chrome
- Firefox
- Safari
- Edge
- Mobile browsers
