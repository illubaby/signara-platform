/**
 * Jira Task Creation Modal - Handles creating Jira tasks via batch file
 */

let jiraTaskCounter = 0;

/**
 * Opens the Create Jira modal and initializes with one task
 */
function openCreateJiraModal() {
    console.log('[openCreateJiraModal] Opening Jira modal');
    const modal = document.getElementById('createJiraModal');
    if (modal) {
        // Reset counter and clear container
        jiraTaskCounter = 0;
        const container = document.getElementById('jiraTasksContainer');
        container.innerHTML = '';
        
        // Add initial task
        addJiraTask();
        
        modal.showModal();
        console.log('[openCreateJiraModal] Modal opened successfully');
    } else {
        console.error('[openCreateJiraModal] Modal element not found');
    }
}

/**
 * Creates a new task form in the modal
 * If there are existing tasks, copies values from the last task
 */
function addJiraTask() {
    console.log('[addJiraTask] Adding new task, counter:', jiraTaskCounter);
    const container = document.getElementById('jiraTasksContainer');
    const taskId = jiraTaskCounter++;
    
    // Get values from previous task if exists
    let previousValues = {};
    if (taskId > 0) {
        const prevTaskId = taskId - 1;
        previousValues = {
            summary: document.getElementById(`summary_${prevTaskId}`)?.value || '',
            brief: document.getElementById(`brief_${prevTaskId}`)?.value || '',
            outcome: document.getElementById(`outcome_${prevTaskId}`)?.value || '',
            assignee: document.getElementById(`assignee_${prevTaskId}`)?.value || '',
            stakeholder: document.getElementById(`stakeholder_${prevTaskId}`)?.value || '',
            labels: document.getElementById(`labels_${prevTaskId}`)?.value || '',
            due_date: document.getElementById(`due_date_${prevTaskId}`)?.value || ''
        };
        console.log('[addJiraTask] Copying values from previous task:', previousValues);
    }
    
    const taskHtml = `
        <div class="card bg-base-100 shadow-md p-4" id="task_${taskId}">
            <div class="flex justify-between items-center mb-3">
                <h4 class="font-semibold">Task ${taskId + 1}</h4>
                <button type="button" onclick="removeJiraTask(${taskId})" class="btn btn-xs btn-error btn-ghost">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    Remove
                </button>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="form-control md:col-span-2">
                    <label class="label">
                        <span class="label-text">Summary *</span>
                    </label>
                    <input type="text" id="summary_${taskId}" placeholder="Task summary" 
                           value="${previousValues.summary || ''}"
                           class="input input-sm input-bordered" required />
                </div>

                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Assignee *</span>
                    </label>
                    <input type="text" id="assignee_${taskId}" placeholder="Assignee username" 
                           value="${previousValues.assignee || ''}"
                           class="input input-sm input-bordered" required />
                </div>                

                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Due Date *</span>
                    </label>
                    <input type="date" id="due_date_${taskId}" 
                           value="${previousValues.due_date || ''}"
                           class="input input-sm input-bordered" required />
                </div>
                
                
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Stakeholder *</span>
                    </label>
                    <input type="text" id="stakeholder_${taskId}" placeholder="Stakeholder username" 
                           value="${previousValues.stakeholder || ''}"
                           class="input input-sm input-bordered" required />
                </div>
                
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Labels</span>
                    </label>
                    <input type="text" id="labels_${taskId}" placeholder="e.g., h213_etm" 
                           value="${previousValues.labels || ''}"
                           class="input input-sm input-bordered" />
                </div>
                
                <div class="form-control md:col-span-2">
                    <label class="label">
                        <span class="label-text">Brief *</span>
                    </label>
                    <textarea id="brief_${taskId}" placeholder="Brief description of the task" 
                              class="textarea textarea-bordered textarea-sm" 
                              rows="2" required>${previousValues.brief || ''}</textarea>
                </div>
                
                <div class="form-control md:col-span-2">
                    <label class="label">
                        <span class="label-text">Outcome *</span>
                    </label>
                    <textarea id="outcome_${taskId}" placeholder="Expected outcome" 
                              class="textarea textarea-bordered textarea-sm" 
                              rows="2" required>${previousValues.outcome || ''}</textarea>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', taskHtml);
    console.log('[addJiraTask] Task added with ID:', taskId);
}

/**
 * Removes a task from the modal
 */
function removeJiraTask(taskId) {
    console.log('[removeJiraTask] Removing task ID:', taskId);
    const taskElement = document.getElementById(`task_${taskId}`);
    if (taskElement) {
        taskElement.remove();
        console.log('[removeJiraTask] Task removed successfully');
        
        // Update task numbers in remaining tasks
        updateTaskNumbers();
    } else {
        console.error('[removeJiraTask] Task element not found:', taskId);
    }
}

/**
 * Updates the display numbers for all tasks after removal
 */
function updateTaskNumbers() {
    const container = document.getElementById('jiraTasksContainer');
    const tasks = container.querySelectorAll('.card');
    tasks.forEach((task, index) => {
        const header = task.querySelector('h4');
        if (header) {
            header.textContent = `Task ${index + 1}`;
        }
    });
    console.log('[updateTaskNumbers] Updated task numbers, total tasks:', tasks.length);
}

/**
 * Collects all task data and submits to backend
 */
async function submitJiraBatch() {
    console.log('[submitJiraBatch] Starting submission');
    
    const container = document.getElementById('jiraTasksContainer');
    const taskElements = container.querySelectorAll('.card');
    
    if (taskElements.length === 0) {
        console.warn('[submitJiraBatch] No tasks to submit');
        alert('Please add at least one task');
        return;
    }
    
    const tasks = [];
    let isValid = true;
    
    // Collect data from all tasks
    taskElements.forEach((taskElement, index) => {
        const taskId = taskElement.id.split('_')[1];
        
        const task = {
            summary: document.getElementById(`summary_${taskId}`)?.value.trim() || '',
            brief: document.getElementById(`brief_${taskId}`)?.value.trim() || '',
            outcome: document.getElementById(`outcome_${taskId}`)?.value.trim() || '',
            assignee: document.getElementById(`assignee_${taskId}`)?.value.trim() || '',
            stakeholder: document.getElementById(`stakeholder_${taskId}`)?.value.trim() || '',
            labels: document.getElementById(`labels_${taskId}`)?.value.trim() || '',
            due_date: document.getElementById(`due_date_${taskId}`)?.value || ''
        };
        
        // Validate required fields
        if (!task.summary || !task.brief || !task.outcome || !task.assignee || !task.stakeholder || !task.due_date) {
            console.error('[submitJiraBatch] Task validation failed:', task);
            alert(`Task ${index + 1} has missing required fields`);
            isValid = false;
            return;
        }
        
        tasks.push(task);
        console.log(`[submitJiraBatch] Task ${index + 1} collected:`, task);
    });
    
    if (!isValid) {
        return;
    }
    
    const environment = document.getElementById('jiraEnvironment')?.value || 'prod';
    
    const requestData = {
        tasks: tasks,
        last_env: environment
    };
    
    console.log('[submitJiraBatch] Sending request:', requestData);
    
    // Get submit button and show loading state
    const submitButton = document.getElementById('jiraSubmitButton');
    const originalButtonContent = submitButton.innerHTML;
    
    // Disable button and show loading
    submitButton.disabled = true;
    submitButton.innerHTML = `
        <span class="loading loading-spinner loading-sm"></span>
        Creating Jira Batch...
    `;
    console.log('[submitJiraBatch] Loading state activated');
    
    try {
        const response = await fetch('/api/jira/create-batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('[submitJiraBatch] Response status:', response.status);
        console.log('[submitJiraBatch] Response headers:', Object.fromEntries(response.headers.entries()));
        
        let result;
        try {
            result = await response.json();
            console.log('[submitJiraBatch] Response data:', result);
        } catch (parseError) {
            console.error('[submitJiraBatch] Failed to parse JSON response:', parseError);
            const text = await response.text();
            console.error('[submitJiraBatch] Raw response text:', text);
            throw new Error(`Invalid JSON response: ${text}`);
        }
        
        if (response.ok && result.success) {
            console.log('[submitJiraBatch] ✅ Success!');
            console.log('[submitJiraBatch] JSON file created at:', result.json_path);
            console.log('[submitJiraBatch] Command executed:', result.command);
            console.log('[submitJiraBatch] Return code:', result.returncode);
            
            if (result.stdout) {
                console.log('[submitJiraBatch] Command stdout:', result.stdout);
            }
            if (result.stderr) {
                console.warn('[submitJiraBatch] Command stderr:', result.stderr);
            }
            
            alert(`Jira batch created successfully!\n\nFile: ${result.json_path}\nCommand: ${result.command}\n\nCheck console for details.`);
            
            // Close modal
            document.getElementById('createJiraModal').close();
        } else {
            // Log full error details
            console.error('[submitJiraBatch] ❌ Failed with status:', response.status);
            console.error('[submitJiraBatch] Error message:', result.message || result.detail);
            console.error('[submitJiraBatch] Full error response:', result);
            
            // Show all available error info
            const errorDetails = result.detail || result.message || result.error || 'Unknown error';
            let alertMessage = `Failed to create Jira batch:\n\n${errorDetails}`;
            
            // Add stdout/stderr if available
            if (result.stdout) {
                alertMessage += `\n\nStdout: ${result.stdout}`;
            }
            if (result.stderr) {
                alertMessage += `\n\nStderr: ${result.stderr}`;
            }
            
            alertMessage += '\n\nCheck console (F12) for full details.';
            alert(alertMessage);
        }
    } catch (error) {
        console.error('[submitJiraBatch] ❌ Error:', error);
        alert(`Error creating Jira batch: ${error.message}\n\nCheck console for details.`);
    } finally {
        // Always restore button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonContent;
        console.log('[submitJiraBatch] Loading state deactivated');
    }
}
