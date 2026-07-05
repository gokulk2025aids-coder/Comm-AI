# 🔧 Quiz Troubleshooting Guide

## Issues Fixed

### ✅ Issue 1: Select Dropdown Not Visible
**Problem**: Question count selector text was invisible (only visible on hover)

**Solution**: Changed the select dropdown to use solid white background with dark text:
- Background: `rgba(255, 255, 255, 0.9)` (solid white)
- Text color: `#333` (dark gray)
- Options also have white background

### ✅ Issue 2: Quiz Not Starting After Clicking Button
**Problem**: Quiz wouldn't load after clicking "Start Quiz"

**Solutions Applied**:
1. Added loading state to button (shows "Loading...")
2. Added comprehensive error handling with console logs
3. Added error messages to help debug
4. Improved API response validation

## 🚀 How to Test

### Step 1: Restart Server
```bash
# Close current terminal
# Run start.bat again
```

### Step 2: Test Quiz Access
1. Open browser: `http://localhost:8000`
2. Login to the app
3. Click "📚 Best Practices" in sidebar
4. Click "📝 Take Email Etiquette Quiz" button
5. You should see the quiz setup page

### Step 3: Check Dropdown Visibility
- The "Number of Questions" dropdown should be clearly visible
- Text should be dark on white background
- Options should be readable

### Step 4: Start Quiz
1. Select number of questions (5, 10, 15, or 20)
2. Click "Start Quiz" button
3. Button should show "Loading..." briefly
4. Quiz questions should appear

### Step 5: Check Browser Console
Press F12 to open Developer Tools and check Console tab for:
- "Loading quiz with X questions..."
- "Quiz loaded: {success: true, questions: [...]}"
- "Displaying question: 1 {question data}"

## 🐛 Common Issues & Solutions

### Issue: Dropdown Still Not Visible
**Solution**:
1. Hard refresh: Press `Ctrl + F5`
2. Clear browser cache
3. Try different browser (Chrome, Firefox, Edge)

### Issue: "Failed to load quiz" Error
**Possible Causes**:
1. Server not running
2. API endpoint not registered
3. Backend file missing

**Solutions**:
1. Check terminal for errors
2. Verify server is running on port 8000
3. Run test script: `python test_quiz_api.py`
4. Check if `backend/email_quiz.py` exists

### Issue: Quiz Loads But Questions Don't Appear
**Check**:
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check if questions array is empty
4. Verify API response in Network tab

### Issue: Can't Submit Quiz
**Check**:
1. Make sure you selected an answer for current question
2. Check browser console for errors
3. Verify all questions have been answered

## 🧪 Testing the Backend

Run the test script to verify backend is working:

```bash
cd c:\Users\ADMIN\OneDrive\Desktop\CommAi
python test_quiz_api.py
```

Expected output:
```
Testing Quiz Endpoints...
==================================================

1. Testing GET /api/quiz/questions?count=5
Status Code: 200
Success: True
Number of questions: 5
First question: What is the ideal length for an email subject line?

2. Testing POST /api/quiz/submit
Status Code: 200
Success: True
Score: 4/5 (80.0%)
Grade: B
Message: Great job! You have strong email skills.

==================================================
Testing complete!
```

## 📋 Checklist

Before reporting issues, verify:

- [ ] Server is running (`start.bat`)
- [ ] No errors in terminal/command prompt
- [ ] Browser is on `http://localhost:8000`
- [ ] Hard refresh done (Ctrl+F5)
- [ ] Browser console checked (F12)
- [ ] Files exist:
  - [ ] `backend/email_quiz.py`
  - [ ] `frontend/quiz.html`
- [ ] API endpoints working (run `test_quiz_api.py`)

## 🔍 Debug Mode

To see detailed logs:

1. Open browser console (F12)
2. Go to Console tab
3. Start the quiz
4. You should see:
   - "Loading quiz with X questions..."
   - "Quiz loaded: {data}"
   - "Displaying question: 1 {data}"
   - "Selected option: X" (when clicking answers)

## 📞 Still Having Issues?

If quiz still doesn't work:

1. **Check server logs** in terminal for errors
2. **Test API directly**:
   - Open: `http://localhost:8000/api/quiz/questions?count=5`
   - Should see JSON with questions
3. **Verify imports** in `backend/main.py`:
   ```python
   from email_quiz import get_all_questions, get_random_questions, check_answer, calculate_score
   ```
4. **Check for Python errors** when starting server

## 🎯 Expected Behavior

### Quiz Setup Page
- Title: "📝 Email Etiquette Quiz"
- Description text visible
- Dropdown with 4 options (5, 10, 15, 20 questions)
- Dropdown text is DARK on WHITE background
- "Start Quiz" button is purple gradient

### During Quiz
- Progress bar shows current question
- Question text is clear
- 4 options (A, B, C, D) are clickable
- Selected option highlights in purple
- "Previous" and "Next" buttons work
- Last question shows "Submit Quiz" button

### Results Page
- Large percentage score
- Letter grade (A-F) with color
- Stats: Correct, Incorrect, Total
- "Review Answers" button
- "Retake Quiz" button
- "Study More" link

---

**All fixes have been applied. Restart your server and try again!** 🚀
