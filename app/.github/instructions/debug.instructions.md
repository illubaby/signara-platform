---
applyTo: '**'
---
## TimeCraft Platform – Debug Guidelines

### Debugging Flow (Trace Request Path)
Follow the 5-layer architecture when debugging:
**Request → Router → Dependency provider → Use case → Port (Protocol) → Infrastructure implementation → Back up stack**

1. **Start from the symptom**: Identify where the issue manifests (UI, API response, backend error)
2. **Move inward through layers**: Trace from Interface → Application → Infrastructure
3. **Isolate the layer**: Determine which layer contains the bug
4. **Fix at the source**: Never patch around issues in the wrong layer

### Python Backend Debugging

**Where Python logs appear:** In the **server terminal** where you run `uvicorn` (NOT in browser F12)

When you run: `python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003`  
All Python `logger` output appears in **that PowerShell/terminal window**.

**Why use `logger` instead of `print()`?**
- ✅ Log levels (DEBUG, INFO, WARNING, ERROR) - filter by severity
- ✅ Automatic timestamps, module names, line numbers
- ✅ Production-ready - can write to files, disable debug logs
- ✅ Structured output for log analysis tools
- ❌ `print()` lacks all of these and clutters output

#### 1. Use Case & Application Layer
- Add strategic logging in use case `execute()` methods
- Log input parameters and return values
- Use Python's `logging` module (already configured in infrastructure)
- Example:
  ```python
  def execute(self, project: str) -> list[str]:
      logger.info(f"ListProjects.execute called with project={project}")  # Shows in SERVER terminal
      result = self.repo.list_projects()
      logger.debug(f"Found {len(result)} projects")  # Shows in SERVER terminal
      return result
  ```

#### 2. Infrastructure Layer
- Log external system interactions (filesystem, Perforce, subprocess calls)
- Capture input/output at integration boundaries
- Log before and after expensive operations
- Example:
  ```python
  def list_projects(self) -> list[str]:
      logger.debug(f"Reading from path: {self.base_path}")
      projects = os.listdir(self.base_path)
      logger.debug(f"Raw projects: {projects}")
      return projects
  ```

#### 3. Router/Interface Layer
- Use FastAPI's logging for request/response debugging
- Log incoming request parameters
- Avoid business logic; if debugging here reveals business issues, move fix inward

#### 4. Testing Strategy
- Write unit tests to isolate bugs (mock ports, assert outputs)
- Use integration tests for infrastructure adapters
- Prefer tests over print statements for reproducibility

### Frontend/JavaScript Debugging

**Where JavaScript logs appear:** In the **browser DevTools Console** (press F12, then Console tab)

This is **completely separate** from Python backend logs. JavaScript runs in the user's browser, Python runs on the server.

#### 1. Browser DevTools
- **Console Tab**: View `console.log()` output, errors, and warnings (F12 → Console)
- **Network Tab**: Inspect API calls, request/response payloads, status codes
- **Sources Tab**: Set breakpoints, step through code
- **Application Tab**: Check localStorage, sessionStorage, cookies

#### 2. Strategic Console Logging
Add `console.log()` statements to trace execution flow and inspect data:

**API Calls & Responses:**
```javascript
async function fetchProjects() {
    console.log('[fetchProjects] Starting API call');
    try {
        const response = await fetch('/api/projects');
        console.log('[fetchProjects] Response status:', response.status);
        const data = await response.json();
        console.log('[fetchProjects] Data received:', data);
        return data;
    } catch (error) {
        console.error('[fetchProjects] Error:', error);
        throw error;
    }
}
```

**Event Handlers:**
```javascript
button.addEventListener('click', (event) => {
    console.log('[ButtonClick] Event triggered:', event);
    console.log('[ButtonClick] Current state:', someStateVariable);
    // handler logic
});
```

**Data Transformations:**
```javascript
function processResults(rawData) {
    console.log('[processResults] Input:', rawData);
    const processed = rawData.map(item => {
        console.log('[processResults] Processing item:', item);
        return transformItem(item);
    });
    console.log('[processResults] Output:', processed);
    return processed;
}
```

**WebSocket/Real-time Updates:**
```javascript
socket.onmessage = (event) => {
    console.log('[WebSocket] Message received:', event.data);
    const parsed = JSON.parse(event.data);
    console.log('[WebSocket] Parsed data:', parsed);
};
```

#### 3. Console Logging Best Practices
- **Use prefixes**: `[FunctionName]` or `[Feature]` to identify log sources
- **Log at boundaries**: Before/after API calls, event handlers, data transformations
- **Log meaningful data**: Include relevant variables, not just "here" or "test"
- **Use appropriate levels**:
  - `console.log()` for general debugging
  - `console.error()` for errors
  - `console.warn()` for warnings
  - `console.debug()` for verbose details
  - `console.table()` for array/object data visualization
- **Clean up before commit**: Remove or comment out debug logs in production code

#### 4. JavaScript File Organization
- Separate JS files in `presentation/static/` (e.g., `app.js`, `app_project_release.js`)
- Never embed complex logic in `<script>` tags within HTML templates
- Keep presentation logic minimal; API calls should only handle UI updates
- When debugging, add logs to the appropriate `.js` file in `presentation/static/`

#### 5. Common Frontend Issues
- **API not responding**: Check Network tab, verify endpoint URL, check CORS
- **Data not displaying**: Log API response, verify data structure matches template expectations
- **Events not firing**: Check event listener registration, verify element selectors
- **State inconsistency**: Log state before/after updates, check for async timing issues
- **WebSocket disconnects**: Log connection status, check reconnection logic

### When to Use Which Logging Tool

| Issue Type | Where to Debug | Tool | Where Logs Appear |
|------------|----------------|------|-------------------|
| API endpoint not returning data | Backend | Python `logger` | Server terminal (uvicorn) |
| Database/file query failing | Backend | Python `logger` | Server terminal (uvicorn) |
| Perforce commands failing | Backend | Python `logger` | Server terminal (uvicorn) |
| Use case logic issues | Backend | Python `logger` | Server terminal (uvicorn) |
| UI not updating correctly | Frontend | `console.log()` | Browser F12 Console |
| Button clicks not working | Frontend | `console.log()` | Browser F12 Console |
| API response not displaying | Frontend | `console.log()` | Browser F12 Console |
| JavaScript errors | Frontend | `console.error()` | Browser F12 Console |

**Example debugging flow:**
1. **UI shows empty list** → Check browser F12 Console: Did API call succeed?
2. **API returned empty array** → Check server terminal: Did backend query find data?
3. **Backend found data** → Check browser F12 Network tab: Was data sent correctly?

### Debugging Checklist

**Before Adding Logs:**
- [ ] Identify the exact symptom and expected behavior
- [ ] Determine if issue is frontend (browser) or backend (server)
- [ ] Locate the request path through the architecture layers
- [ ] Determine which layer likely contains the bug

**When Adding Debug Code:**
- [ ] Python: Use `logging` module, not `print()` statements
- [ ] JavaScript: Use `console.log()` with clear prefixes
- [ ] Log at integration boundaries (API calls, external system access)
- [ ] Log input parameters and output results
- [ ] Capture error details with full context

**After Fixing:**
- [ ] Remove or reduce verbose debug logging
- [ ] Add focused unit/integration test to prevent regression
- [ ] Verify fix doesn't break other features
- [ ] Update documentation if behavior changed

### Anti-Patterns to Avoid
- ❌ Adding business logic to routers/templates to work around bugs
- ❌ Calling infrastructure directly from use cases without ports
- ❌ Using `print()` instead of proper logging in Python
- ❌ Leaving extensive debug logs in production code
- ❌ Embedding debug JS logic in HTML `<script>` tags
- ❌ Making assumptions without verification—always trace execution
- ❌ Patching symptoms instead of fixing root causes

### Tools & Commands
- **Backend logs**: Check terminal where `uvicorn` is running
- **Test specific feature**: `pytest tests/unit/test_<feature>.py -v`
- **Browser DevTools**: F12 or Right-click → Inspect
- **Network inspection**: DevTools → Network tab → Preserve log
- **Clear cache**: Hard refresh (Ctrl+Shift+R) to avoid stale JS/CSS

---
**Key Principle**: Debug systematically by following the architecture. Logs should illuminate the request flow, not clutter it. Always clean up debug code before committing.