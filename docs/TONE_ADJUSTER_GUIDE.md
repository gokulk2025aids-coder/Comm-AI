# Tone Adjuster Troubleshooting Guide

## ✅ Feature Status: WORKING

The Tone Adjuster has been successfully implemented and tested.

## How to Use:

1. **Start the Server**
   - Run `start.bat` (Windows) or `python -m uvicorn main:app --reload --port 8000` from the backend folder
   - Wait for the server to start completely

2. **Access the Feature**
   - Open http://localhost:8000 in your browser
   - Login with your credentials
   - Click "Tone Adjuster" in the sidebar (🎨 icon)

3. **Use the Tool**
   - Paste your email text in the "Original Text" box
   - Choose one of the quick conversions:
     - **Casual → Formal**: Transforms informal language to professional
     - **Aggressive → Diplomatic**: Softens harsh language
   - OR use the **Formality Level Slider** (0-100) and click "Apply Formality Level"
   - View the adjusted text in the preview section
   - Copy or use the adjusted text in the Email Analyzer

## Common Issues & Solutions:

### Issue 1: "Error" message when clicking conversion buttons
**Solution:**
- Make sure the server is running (check terminal/command prompt)
- Verify you're logged in
- Check browser console (F12) for detailed error messages
- Ensure text is at least 5 characters long

### Issue 2: Server not starting
**Solution:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Issue 3: Import errors
**Solution:**
- Ensure `tone_adjuster.py` is in the `backend` folder
- Restart the server after adding new files

### Issue 4: No response from server
**Solution:**
- Check if port 8000 is already in use
- Try a different port: `python -m uvicorn main:app --reload --port 8001`
- Update API_URL in `frontend/app.js` to match the new port

## Testing the Backend:

Run this command from the CommAi folder:
```bash
cd backend
python test_tone_adjuster.py
```

You should see successful test results for all 5 tests.

## API Endpoint:

**POST** `/api/adjust-tone`

**Request Body:**
```json
{
  "text": "hey there! thanks for the email",
  "conversion_type": "casual_to_formal",
  "formality_level": 50
}
```

**Response:**
```json
{
  "success": true,
  "adjusted_text": "Dear there. Thank you for the email",
  "conversion_type": "casual_to_formal"
}
```

## Conversion Types:
- `casual_to_formal` - Makes text more professional
- `aggressive_to_diplomatic` - Softens harsh language
- `formality_slider` - Adjusts based on formality_level (0-100)

## Browser Console Debugging:

If you see errors, open browser console (F12) and check:
1. Network tab - Look for failed requests to `/api/adjust-tone`
2. Console tab - Look for JavaScript errors
3. Check the request payload and response

## Server Logs:

Check `backend/commai.log` for detailed server-side errors.

## Need More Help?

1. Restart the server completely
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try a different browser
4. Check if all files are in the correct locations:
   - `backend/tone_adjuster.py` ✓
   - `backend/main.py` (updated with endpoint) ✓
   - `frontend/index.html` (updated with UI) ✓
   - `frontend/app.js` (updated with functionality) ✓
   - `frontend/app.css` (updated with styles) ✓
