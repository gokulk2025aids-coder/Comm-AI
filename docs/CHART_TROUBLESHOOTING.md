# Visual Analysis Charts - Troubleshooting Guide

## Issue: Charts Not Visible

### Diagnostic Steps

#### Step 1: Test Chart.js Loading
1. Open browser and go to: `http://localhost:8000/static/chart-test.html`
2. Check if you see:
   - ✅ "Chart.js is loaded! Version: X.X.X"
   - ✅ "Test chart created successfully!"
   - A colorful bar chart displayed

**If test page works:**
- Chart.js is loading correctly
- Issue is in the main application
- Proceed to Step 2

**If test page fails:**
- Chart.js file may be corrupted
- Check browser console (F12) for errors
- Re-download Chart.js (see Step 5)

---

#### Step 2: Check Browser Console
1. Open the main app: `http://localhost:8000`
2. Login and analyze an email
3. Press F12 to open Developer Tools
4. Go to "Console" tab
5. Look for messages starting with "generateCharts"

**Expected console output:**
```
generateCharts called with analysis: {Object}
Chart.js is loaded, version: 4.4.0
Theme: dark
Radar canvas found: <canvas>
Radar chart scores: {Object}
Radar chart created successfully
Bar canvas found: <canvas>
Bar chart created successfully
Pie canvas found: <canvas>
Pie chart created successfully
All charts generated successfully
```

**If you see errors:**
- Note the exact error message
- Check which chart is failing
- See common errors below

---

#### Step 3: Check Canvas Elements
In browser console (F12), type:
```javascript
document.getElementById('radarChart')
document.getElementById('barChart')
document.getElementById('pieChart')
```

**Expected:** Each should return `<canvas id="..."></canvas>`
**If null:** Canvas elements are missing from HTML

---

#### Step 4: Force Chart Regeneration
In browser console, type:
```javascript
if (currentAnalysis) {
    generateCharts(currentAnalysis);
}
```

This will attempt to regenerate charts with debug output.

---

#### Step 5: Re-download Chart.js
If Chart.js is corrupted:

**Windows:**
```cmd
cd c:\Users\ADMIN\OneDrive\Desktop\CommAi\frontend
curl -o chart.min.js https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
```

**Or manually:**
1. Go to: https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
2. Save file as `chart.min.js` in `frontend` folder

---

### Common Errors & Solutions

#### Error: "Chart.js is not loaded"
**Cause:** Chart.js file not loading
**Solution:**
1. Check file exists: `frontend/chart.min.js`
2. Check file size: Should be ~200KB
3. Re-download if corrupted
4. Clear browser cache (Ctrl+Shift+Delete)

#### Error: "Canvas not found"
**Cause:** HTML elements missing
**Solution:**
1. Check `index.html` has canvas elements
2. Restart server
3. Hard refresh browser (Ctrl+Shift+R)

#### Error: "Cannot read property 'getContext'"
**Cause:** Canvas element not ready
**Solution:**
- Already fixed with 100ms delay in displayResults()
- If still occurs, increase delay to 200ms

#### Charts show but are tiny/invisible
**Cause:** CSS sizing issue
**Solution:**
1. Check CSS has proper chart-box styling
2. Verify min-height: 450px
3. Check display: block on canvas

---

### Quick Fixes

#### Fix 1: Clear Everything and Restart
```cmd
1. Stop server (Ctrl+C)
2. Clear browser cache (Ctrl+Shift+Delete)
3. Restart server (start.bat)
4. Hard refresh browser (Ctrl+Shift+R)
```

#### Fix 2: Force Chart Visibility
Add to browser console:
```javascript
document.querySelectorAll('.chart-box').forEach(box => {
    box.style.display = 'flex';
    box.style.minHeight = '450px';
    box.style.visibility = 'visible';
});
```

#### Fix 3: Check Results Section
```javascript
document.getElementById('results-section').style.display
// Should return: "block"
```

---

### Debugging Checklist

- [ ] Server is running on port 8000
- [ ] Logged in successfully
- [ ] Email analyzed (results showing)
- [ ] Scrolled down to Visual Analysis section
- [ ] Chart.js test page works
- [ ] Browser console shows no errors
- [ ] Canvas elements exist in DOM
- [ ] CSS is loaded properly
- [ ] No browser extensions blocking scripts

---

### Files to Check

1. **frontend/chart.min.js**
   - Size: ~200KB
   - Should not be empty

2. **frontend/index.html**
   - Line 7: `<script src="/static/chart.min.js"></script>`
   - Canvas elements with IDs: radarChart, barChart, pieChart

3. **frontend/app.js**
   - generateCharts() function exists
   - Called from displayResults() with 100ms delay

4. **frontend/app.css**
   - .charts-container styling
   - .chart-box min-height: 450px
   - canvas display: block

---

### Still Not Working?

1. **Check browser compatibility:**
   - Use Chrome, Firefox, or Edge (latest version)
   - Disable browser extensions
   - Try incognito/private mode

2. **Check network:**
   - Open Network tab in DevTools (F12)
   - Reload page
   - Check if chart.min.js loads (Status: 200)

3. **Check JavaScript errors:**
   - Any red errors in console?
   - Any warnings about Chart?

4. **Test with simple email:**
   ```
   Dear Team,
   
   This is a test email to check the analysis.
   
   Best regards,
   John
   ```

---

### Enhanced Debugging (Added)

The latest update includes:
- ✅ Comprehensive console logging
- ✅ Error catching for each chart
- ✅ Chart.js version display
- ✅ Canvas element validation
- ✅ Context creation verification
- ✅ Score calculation logging

**To see debug output:**
1. Open console (F12)
2. Analyze an email
3. Watch for detailed logs
4. Report any errors you see

---

### Contact Information

If charts still don't work after all steps:
1. Note the exact error from console
2. Check which step failed
3. Verify all files are present
4. Try the test page first

---

**Last Updated:** Latest version with enhanced debugging
**Status:** Comprehensive troubleshooting added
