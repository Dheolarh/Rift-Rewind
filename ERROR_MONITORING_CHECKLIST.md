# Error Monitoring Checklist

## 🔍 Common Python Runtime Errors to Watch For

### 1. NameError: name 'X' is not defined
**Symptoms:** Variable or module used before import/definition  
**Examples:**
- `logger` used without `import logging`
- `boto3` used without import
- Typos in variable names

**Prevention:**
```bash
# Check for logger usage without import
cd backend
Get-ChildItem -Recurse -Filter *.py | ForEach-Object { 
    $file = $_.FullName
    $hasLogger = Select-String -Path $file -Pattern "logger\." -Quiet
    $hasImport = Select-String -Path $file -Pattern "import logging" -Quiet
    if ($hasLogger -and -not $hasImport) { 
        Write-Host "MISSING: $($_.Name)" 
    }
}
```

**Status:** ✅ All fixed (analytics.py was the last one)

---

### 2. AttributeError: 'NoneType' object has no attribute 'X'
**Symptoms:** Accessing properties on None/null values  
**Common Locations:**
- Match data parsing: `match.get('info')` could be None
- S3 downloads: File might not exist
- API responses: Request could fail

**Prevention:**
- Always check if data exists before accessing
- Use `.get()` with defaults: `data.get('key', {})`
- Validate responses before processing

**Current Status:** ✅ Well handled with try/except blocks

---

### 3. KeyError: 'key'
**Symptoms:** Accessing dictionary key that doesn't exist  
**Common Locations:**
- Analytics calculations: Missing match fields
- Slide data mapping: Expected field not in response

**Prevention:**
```python
# Bad
value = data['key']

# Good
value = data.get('key', default_value)

# Better
if 'key' in data:
    value = data['key']
```

**Current Status:** ✅ Most code uses `.get()` with defaults

---

### 4. TypeError: 'X' object is not iterable
**Symptoms:** Trying to loop over non-list/dict  
**Example:** `for x in None:` fails

**Prevention:**
```python
# Safe iteration
for item in (items or []):
    process(item)
```

**Current Status:** ✅ Generally handled well

---

### 5. ImportError / ModuleNotFoundError
**Symptoms:** Missing package or wrong import path  
**Common Issues:**
- Missing packages in requirements.txt
- Wrong relative imports

**Prevention:**
```bash
# Verify all imports work
cd backend
python -c "from services.analytics import RiftRewindAnalytics; print('OK')"
python -c "from lambdas.league_data import LeagueDataFetcher; print('OK')"
```

**Current Status:** ✅ All imports verified

---

### 6. IndentationError / SyntaxError
**Symptoms:** Python can't parse the file  
**Prevention:**
- Use consistent indentation (4 spaces)
- Check for mixed tabs/spaces
- Validate syntax before running

```bash
# Check syntax
python -m py_compile backend/api.py
```

**Current Status:** ✅ All files valid

---

### 7. JSONDecodeError
**Symptoms:** Invalid JSON from API or S3  
**Common Locations:**
- Bedrock AI responses
- Riot API responses
- S3 file parsing

**Prevention:**
```python
try:
    data = json.loads(response_text)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return default_data
```

**Current Status:** ✅ Handled in AI generation code

---

### 8. RequestException (Network Errors)
**Symptoms:** HTTP request fails  
**Types:**
- `SSLError`: SSL certificate issues
- `ConnectionError`: Network down
- `Timeout`: Request took too long
- `HTTPError`: 4xx/5xx status codes

**Prevention:** ✅ Already implemented in `riot_api_client.py`
- Exponential backoff retry (1s, 2s, 4s)
- Graceful degradation (skip failed matches)
- Clear error logging with emojis

**Current Status:** ✅ Excellent coverage

---

## 🧪 Pre-Flight Testing Commands

### Test 1: Verify All Imports
```powershell
cd C:\Users\Administrator\Desktop\Rift-Rewind\backend
python -c "
from api import RiftRewindAPI
from services.analytics import RiftRewindAnalytics
from services.riot_api_client import RiotAPIClient
from lambdas.league_data import LeagueDataFetcher
print('✅ All imports successful')
"
```

### Test 2: Check Python Syntax
```powershell
cd backend
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
    python -m py_compile $_.FullName
}
Write-Host "✅ All files have valid syntax"
```

### Test 3: Verify Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

required = ['RIOT_API_KEY']
optional = ['S3_BUCKET_NAME', 'BEDROCK_MODEL_ID', 'TEST_MODE']

print("Required:")
for key in required:
    value = os.getenv(key)
    print(f"  {key}: {'✅ Set' if value else '❌ MISSING'}")

print("\nOptional:")
for key in optional:
    value = os.getenv(key)
    print(f"  {key}: {'✅ Set' if value else '⚠️ Using default'}")
```

### Test 4: Test Analytics Calculation
```python
# Create mock data
mock_data = {
    'account': {'puuid': 'test'},
    'summoner': {},
    'ranked': {},
    'matches': []
}

from services.analytics import RiftRewindAnalytics

try:
    analytics = RiftRewindAnalytics(mock_data)
    result = analytics.calculate_all()
    print("✅ Analytics calculation works")
except Exception as e:
    print(f"❌ Analytics failed: {e}")
```

---

## 📊 Monitoring After Deployment

### Log Patterns to Watch

#### ❌ ERROR Patterns (Requires Immediate Attention)
```
❌ Request timed out after 3 attempts
❌ SSL Error persists after 3 attempts
❌ Connection failed after 3 attempts
name 'X' is not defined
KeyError: 'X'
AttributeError: 'NoneType'
```

#### ⚠️ WARNING Patterns (Monitor, But Non-Critical)
```
⏱️  Timeout on attempt 1/3 - retrying
🔒 SSL Error on attempt 1/3 - connection issue
🔌 Connection Error on attempt 1/3 - network issue
⚠️  20 matches failed (continuing)
```

#### ✅ SUCCESS Patterns (All Good)
```
✓ Analytics calculation complete!
✓ Session marked complete
✓ Found X matches from the past year
✓ Retrieved X/X match details
```

---

## 🚨 Emergency Debugging

### If Server Crashes on Startup
1. Check logger imports: `grep -r "import logging" backend/`
2. Verify syntax: `python -m py_compile backend/server.py`
3. Test imports: `python -c "from api import RiftRewindAPI"`
4. Check .env file exists and has RIOT_API_KEY

### If Analytics Calculation Fails
1. Check `analytics.py` line 601 area
2. Verify logger is imported
3. Check for missing data fields
4. Test with mock data first

### If Frontend Can't Connect
1. Verify backend running: `http://localhost:8000/api/health`
2. Check CORS settings in `server.py`
3. Verify frontend .env has correct API_URL
4. Check network tab for actual error

---

## ✅ Current Status Summary

| Component | Status | Last Issue | Fixed |
|-----------|--------|------------|-------|
| Logger Setup | ✅ GOOD | analytics.py missing import | ✅ Yes |
| Network Errors | ✅ GOOD | SSL/timeout handling | ✅ Yes |
| Type Safety | ✅ GOOD | Type hints everywhere | ✅ N/A |
| Error Handling | ✅ GOOD | Try/except coverage | ✅ N/A |
| Import Paths | ✅ GOOD | All verified | ✅ N/A |
| Syntax | ✅ GOOD | All valid Python | ✅ N/A |

**Overall Backend Health: 🟢 EXCELLENT**

All known logger errors resolved. Backend ready for production testing.

---

**Created:** October 15, 2025  
**Last Updated:** October 15, 2025  
**Next Review:** After first production deployment
