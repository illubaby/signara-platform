// Example: How to use ExecutionStreamFactory in new pages
// For reference - QC page still uses legacy approach for backward compatibility

/* 
==============================================
EXAMPLE 1: Simple Usage (Minimal Config)
==============================================
Callbacks (onStart, onComplete, onError) are OPTIONAL!
Factory has smart defaults - just provide the essentials.
*/

// In your template:
// {% from 'components/execution_output.html' import execution_output %}
// {{ execution_output(title='Build Script', container_id='buildExecution') }}
// 
// <script src="{{ url_for('static', path='/js/shared/websocket_output_stream.js') }}"></script>
// <script src="{{ url_for('static', path='/js/shared/execution_stream_factory.js') }}"></script>

// In your JavaScript (MINIMAL - only 4 lines!):
function runBuildScript() {
  ExecutionStreamFactory.create({
    executionDir: '/project/build',
    command: '/project/build/compile.sh',
    containerId: 'buildExecution'
  }).connect(); // That's it! Shell defaults to /bin/bash
}

// If you need callbacks, add them:
function runBuildScriptWithCallbacks() {
  const stream = ExecutionStreamFactory.create({
    executionDir: '/project/build',
    command: '/project/build/compile.sh',
    containerId: 'buildExecution',
    
    // Optional callbacks:
    onComplete: (result) => {
      if (result.success) {
        alert('Build successful!');
      }
    }
  });
  
  stream.connect();
  return stream; // Keep reference for stop() if needed
}

/*
==============================================
EXAMPLE 2: Multiple Execution Streams (Chaining)
==============================================
*/

// Template with multiple containers:
// {{ execution_output(title='Compile', container_id='compileExecution') }}
// {{ execution_output(title='Test', container_id='testExecution') }}

function runCompile() {
  ExecutionStreamFactory.create({
    executionDir: '/project',
    command: '/project/compile.sh',
    containerId: 'compileExecution',
    
    // Only add callback if you need to chain commands:
    onComplete: (r) => {
      if (r.success) runTests(); // Auto-run tests after successful compile
    }
  }).connect();
}

function runTests() {
  ExecutionStreamFactory.create({
    executionDir: '/project',
    command: '/project/test.sh',
    containerId: 'testExecution'
  }).connect(); // No callbacks needed if just running independently
}

/*
==============================================
EXAMPLE 3: Custom WebSocket Endpoint
==============================================
For features with custom WebSocket endpoints (like SAF, QC),
just build your own URL and pass it via wsBaseUrl.
*/

// SAF Feature Example - Build custom WebSocket URL:
function runSafCell(project, subproject, cell, cellType) {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  const wsUrl = `${protocol}://${location.host}/api/saf/${project}/${subproject}/cells/${cell}/execute/ws?cell_type=${cellType}`;
  
  ExecutionStreamFactory.create({
    executionDir: 'N/A', // Will be updated from server response
    command: 'N/A',      // Will be updated from server response
    containerId: 'executionOutputGroup',
    wsBaseUrl: wsUrl,    // Custom WebSocket endpoint
    
    // Optional callbacks for feature-specific logic:
    onComplete: () => {
      // Refresh status after execution
      if (global.SAFPvtStatus) {
        global.SAFPvtStatus.refreshStatuses();
      }
    }
  }).connect();
}

// QC Feature Example:
function runQcExecution(project, subproject, cell) {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  const wsUrl = `${protocol}://${location.host}/api/qc/${project}/${subproject}/run-script/ws?cell=${encodeURIComponent(cell)}`;
  
  ExecutionStreamFactory.create({
    executionDir: 'N/A',
    command: 'N/A',
    containerId: 'executionOutputGroup',
    wsBaseUrl: wsUrl
  }).connect();
}

/*
==============================================
EXAMPLE 4: Direct WebSocketOutputStream (Advanced)
==============================================
*/

// For maximum control, use WebSocketOutputStream directly (like QC does):
function advancedUsage() {
  const stream = new WebSocketOutputStream({
    outputElement: document.getElementById('myOutput'),
    autoScrollElement: document.getElementById('myAutoscroll'),
    statusElement: document.getElementById('myStatus'),
    elapsedElement: document.getElementById('myElapsed'),
    wsUrl: 'ws://localhost:8000/api/custom/endpoint',
    
    onOpen: () => console.log('Started'),
    onMessage: (msg) => console.log('Message', msg),
    onComplete: (result) => console.log('Done', result),
    onError: (error) => console.error('Error', error),
    onClose: () => console.log('Closed')
  });
  
  stream.connect();
  
  // Can stop manually
  document.getElementById('stopBtn').onclick = () => stream.stop();
  
  // Can clear output
  document.getElementById('clearBtn').onclick = () => stream.clearOutput();
}

/*
==============================================
KEY PRINCIPLES
==============================================

1. **Factory is generic** - No feature-specific presets (no SAF, QC presets)
2. **Callbacks are optional** - Factory handles all standard UI updates
3. **Custom endpoints via wsBaseUrl** - Build your own WebSocket URL for feature-specific endpoints
4. **Keep it simple** - Only define what's NOT standard behavior

The factory provides a clean, reusable abstraction. Features configure their own URLs!

*/
