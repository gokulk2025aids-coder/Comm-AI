# 🔧 Reports Feature - Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "Failed to generate report" message but report appears

**Symptoms:**
- Error toast shows "Failed to generate report"
- Report actually displays correctly
- All data is visible

**Cause:**
- Network response handling issue
- Response status check too strict

**Solution:**
✅ **FIXED** - Updated error handling to check response.ok properly

**What was changed:**
- Added `if (!response.ok)` check before parsing JSON
- Better error logging in frontend
- Improved backend error responses

---

### Issue 2: Score Trends Chart not visible

**Symptoms:**
- Chart section shows but canvas is blank
- "Not enough data" message appears
- Chart.js loaded but not rendering

**Possible Causes:**
1. Not enough emails analyzed in the period
2. Chart.js not loaded properly
3. Canvas element not found
4. Data structure mismatch

**Solutions:**

#### Solution A: Analyze More Emails
```
Minimum Required: 1 email
Recommended: 5+ emails for meaningful trends
```

**Steps:**
1. Go to Email Analyzer
2. Analyze at least 5 emails
3. Wait a few minutes (ensure timestamps are in period)
4. Generate report again

#### Solution B: Check Chart.js
```javascript
// Open browser console (F12)
// Type: typeof Chart
// Should return: "function"
// If "undefined", Chart.js not loaded
```

**Fix:**
1. Refresh the page (F5)
2. Clear browser cache (Ctrl+Shift+Del)
3. Check internet connection
4. Try different browser

#### Solution C: Verify Data
✅ **FIXED** - Added better error handling and logging

**What was changed:**
- Added try-catch around chart creation
- Better empty data handling
- Fallback message if chart fails
- Console logging for debugging

---

### Issue 3: PDF Download Error

**Symptoms:**
- "Failed to download PDF" toast
- Console shows error
- No PDF file downloaded

**Possible Causes:**
1. Backend PDF generation error
2. Network timeout
3. Browser pop-up blocker
4. Missing report data

**Solutions:**

#### Solution A: Check Report Data
```
Before downloading PDF:
1. Ensure report is fully loaded
2. All sections should be visible
3. Wait for chart to render
4. Then click Download PDF
```

#### Solution B: Check Browser Console
```javascript
// Open console (F12)
// Look for errors like:
// - "Failed to generate PDF"
// - Network errors
// - CORS errors
```

**Common Fixes:**
- ✅ Disable pop-up blocker for localhost
- ✅ Check backend server is running
- ✅ Verify report data is complete
- ✅ Try different browser

#### Solution C: Backend Logs
```bash
# Check backend terminal for errors
# Look for:
# - "PDF report generation error"
# - "Error generating report PDF"
# - Traceback information
```

✅ **FIXED** - Improved PDF generation:
- Better error handling
- Detailed logging
- Safer text encoding
- Limited text lengths to prevent overflow

---

### Issue 4: Empty Report / No Data

**Symptoms:**
- Report shows "No data available"
- All sections empty
- Chart not displayed

**Cause:**
No emails analyzed in the selected period

**Solution:**

#### Check Analysis History:
1. Go to History tab
2. Check timestamps of analyses
3. Ensure analyses are within:
   - Last 7 days (for weekly)
   - Last 30 days (for monthly)

#### Analyze New Emails:
1. Go to Email Analyzer
2. Analyze 5-10 emails
3. Wait a moment
4. Generate report again

#### Verify Period Selection:
- Weekly = Last 7 days only
- Monthly = Last 30 days only
- Older analyses won't appear

---

### Issue 5: Chart Shows Wrong Data

**Symptoms:**
- Chart displays but data looks incorrect
- Scores don't match table
- Missing data points

**Cause:**
Data structure mismatch or calculation error

**Solution:**

✅ **FIXED** - Improved data handling:
- Proper score extraction
- Safe array access
- Default values for missing data
- Better error messages

**Verification Steps:**
1. Check browser console for errors
2. Verify all emails have scores
3. Ensure analyses are complete
4. Regenerate report

---

## 🔍 Debugging Steps

### Step 1: Check Browser Console
```
1. Press F12 to open DevTools
2. Go to Console tab
3. Look for red errors
4. Note any error messages
```

**Common Errors:**
- `Chart is not defined` → Chart.js not loaded
- `Cannot read property` → Data structure issue
- `Network error` → Backend not responding
- `404 Not Found` → API endpoint issue

### Step 2: Check Network Tab
```
1. Open DevTools (F12)
2. Go to Network tab
3. Click "Generate Report"
4. Check API calls:
   - /api/reports/generate
   - /api/reports/download-pdf
```

**What to Look For:**
- Status: Should be 200 (OK)
- Response: Should have JSON data
- Time: Should be < 5 seconds
- Size: Should have content

### Step 3: Check Backend Logs
```
Look in terminal/console where backend is running
Check for:
- "Report generated successfully"
- "PDF report generated successfully"
- Any error messages
- Traceback information
```

### Step 4: Verify Data
```javascript
// In browser console, after generating report:
console.log(currentReportData);

// Should show:
// - success: true
// - summary: {...}
// - score_breakdown: {...}
// - All sections populated
```

---

## 🛠️ Quick Fixes

### Fix 1: Refresh Everything
```
1. Close all browser tabs
2. Restart backend server
3. Open new browser tab
4. Login again
5. Try generating report
```

### Fix 2: Clear Cache
```
1. Press Ctrl+Shift+Del
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page (F5)
5. Try again
```

### Fix 3: Use Different Browser
```
Try in order:
1. Chrome (recommended)
2. Firefox
3. Edge
4. Safari
```

### Fix 4: Check Requirements
```bash
# Ensure all dependencies installed:
pip install -r requirements.txt

# Verify fpdf2 is installed:
pip show fpdf2

# Should show version 2.7.0 or higher
```

---

## 📊 Data Requirements

### Minimum Requirements:
- ✅ At least 1 email analyzed
- ✅ Analysis within period (7 or 30 days)
- ✅ Complete analysis data
- ✅ Valid user session

### Recommended:
- ✅ 5+ emails for trends
- ✅ 10+ emails for accurate insights
- ✅ Regular analysis (daily/weekly)
- ✅ Variety of email types

---

## 🚨 Error Messages Explained

### "Failed to generate report"
**Meaning:** Backend couldn't create report
**Fix:** Check if you have analyzed emails in the period

### "No data available for this period"
**Meaning:** No analyses found in timeframe
**Fix:** Analyze emails first, then generate report

### "Failed to download PDF"
**Meaning:** PDF generation failed
**Fix:** Check backend logs, ensure report data is complete

### "Not enough data to display trends chart"
**Meaning:** Insufficient data points for chart
**Fix:** Analyze more emails (minimum 1, recommended 5+)

### "Error displaying chart"
**Meaning:** Chart.js rendering failed
**Fix:** Refresh page, check console for errors

---

## ✅ Verification Checklist

Before reporting an issue, verify:

- [ ] Backend server is running
- [ ] Logged in successfully
- [ ] Analyzed emails in the period
- [ ] Browser console shows no errors
- [ ] Internet connection is stable
- [ ] Using supported browser (Chrome/Firefox/Edge)
- [ ] Chart.js is loaded (check console: `typeof Chart`)
- [ ] No pop-up blocker for PDF downloads
- [ ] Sufficient disk space for downloads

---

## 📞 Still Having Issues?

If problems persist after trying all solutions:

1. **Collect Information:**
   - Browser console errors (screenshot)
   - Backend terminal logs (copy text)
   - Steps to reproduce
   - Expected vs actual behavior

2. **Check Documentation:**
   - REPORTS_FEATURE_GUIDE.md
   - README.md
   - QUICK_REFERENCE.md

3. **Try Clean Install:**
   ```bash
   # Backup your database
   # Reinstall dependencies
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   # Restart server
   ```

---

## 🎯 Prevention Tips

### To Avoid Issues:
1. ✅ Analyze emails regularly
2. ✅ Generate reports weekly
3. ✅ Keep browser updated
4. ✅ Clear cache monthly
5. ✅ Check logs periodically
6. ✅ Backup important reports (download PDFs)

### Best Practices:
1. ✅ Analyze 5-10 emails before generating report
2. ✅ Wait for all sections to load before downloading PDF
3. ✅ Use Chrome or Firefox for best compatibility
4. ✅ Keep backend server running while using app
5. ✅ Don't close browser during PDF generation

---

**Most issues are now fixed in the latest version! 🎉**

If you encounter any new issues, check the browser console and backend logs for detailed error messages.
