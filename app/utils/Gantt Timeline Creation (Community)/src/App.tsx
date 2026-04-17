import { useState, useMemo, useEffect } from 'react';
import { GanttChart } from './components/gantt-chart';
import { TeamOverview } from './components/team-overview';
import { TaskFilters } from './components/task-filters';
import { ProjectStats } from './components/project-stats';
import { Button } from './components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './components/ui/dialog';
import { Label } from './components/ui/label';
import { Input } from './components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Checkbox } from './components/ui/checkbox';
import { Calendar, Users, BarChart3, Plus, Upload, RefreshCw, Settings, Search } from 'lucide-react';

type CellStatusCategory = {
  total: number;
  completed: number;
};

type ProjectCellStatus = {
  project: string;
  subproject: string;
  sis: CellStatusCategory;
  nt: CellStatusCategory;
  int: CellStatusCategory;
  overall_completion: number;
};

type TeamMap = { [key: string]: { name: string; color: string; members: string[] } };
type TaskItem = {
  id: string;
  name: string; // base task name
  startDate: Date;
  endDate: Date;
  progress: number;
  team: string; // primary team for grouping
  teamTags?: string[]; // all involved teams
  assignees: string[];
  color: string;
  milestone?: string;
  baseName?: string;
  rel?: string;
  note?: string; // User notes for this task
  cellStatus?: ProjectCellStatus; // Item completion data
};

const TEAM_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#22c55e"];
const MILESTONE_COLORS: Record<string, string> = {
  prelim: "#3b82f6",
  prefinal: "#f59e0b",
  final: "#22c55e",
  swap_gds: "#8b5cf6",
};

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTeam, setSelectedTeam] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [teams, setTeams] = useState<TeamMap>({});
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [addOpen, setAddOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [changeLog, setChangeLog] = useState<string[]>([]); // Track changes during edit mode
  
  // Manage Projects state
  const [manageProjectsOpen, setManageProjectsOpen] = useState(false);
  const [hiddenProjects, setHiddenProjects] = useState<Set<string>>(new Set());
  const [allProjectNames, setAllProjectNames] = useState<string[]>([]); // All project names from JSON
  const [projectSearchTerm, setProjectSearchTerm] = useState('');
  
  // Edit Task state
  const [editOpen, setEditOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskItem | null>(null);
  const [editStart, setEditStart] = useState('');
  const [editEnd, setEditEnd] = useState('');
  const [editRel, setEditRel] = useState('');
  const [editEtm, setEditEtm] = useState('');
  const [editInt, setEditInt] = useState('');
  const [editCkt, setEditCkt] = useState('');
  const [editNote, setEditNote] = useState('');

  // Add Task Form state
  const [newTaskName, setNewTaskName] = useState('');
  const [etmLead, setEtmLead] = useState('');
  const [intLead, setIntLead] = useState('');
  const [cktLead, setCktLead] = useState('');
  const milestoneKeys = ['prelim', 'prefinal', 'final', 'swap_gds'] as const;
  const [milestoneDates, setMilestoneDates] = useState<Record<string, { start: string; end: string; rel: string; note: string }>>({
    prelim: { start: '', end: '', rel: '', note: '' },
    prefinal: { start: '', end: '', rel: '', note: '' },
    final: { start: '', end: '', rel: '', note: '' },
    swap_gds: { start: '', end: '', rel: '', note: '' },
  });

  // Extract loadData as a separate function so it can be called on refresh
  // refreshFromP4: when true, forces download of individual project files from P4
  const loadData = async (refreshFromP4: boolean = false) => {
    try {
      setLoading(true);
      // Add cache busting timestamp to prevent browser caching
      const timestamp = new Date().getTime();
      const [statusRes, teamRes] = await Promise.all([
        fetch(`/cache/global_project_status.json?t=${timestamp}`),
        fetch(`/cache/timing_team.json?t=${timestamp}`),
      ]);
      const statusJson = await statusRes.json();
      const timingTeams = await teamRes.json();

      // Load hidden projects from JSON and track all project names
      const hiddenSet = new Set<string>();
      const allNames = new Set<string>();
      (statusJson || []).forEach((item: any) => {
        const taskName = String(item.task || '');
        if (taskName) {
          allNames.add(taskName);
          if (item.hidden === true) {
            hiddenSet.add(taskName);
          }
        }
      });
      setHiddenProjects(hiddenSet);
      setAllProjectNames(Array.from(allNames).sort());

      // Build teams map with colors
      const teamMap: TeamMap = {};
      (timingTeams || []).forEach((t: { team: string; members: string[] }, idx: number) => {
        teamMap[t.team] = {
          name: t.team,
          color: TEAM_COLORS[idx % TEAM_COLORS.length],
          members: t.members,
        };
      });

      // Helper: resolve all teams that contain any lead name
      function resolveTeamsForLeads(leads: string[]): string[] {
        const tags = new Set<string>();
        for (const [teamName, teamInfo] of Object.entries(teamMap)) {
          const members = (teamInfo.members || []).map(m => String(m).trim());
          for (const lead of leads) {
            const name = String(lead || '').trim();
            if (!name) continue;
            if (members.includes(name)) {
              tags.add(teamName);
            }
          }
        }
        return Array.from(tags);
      }

      // Map status JSON to chart tasks (multi-team support)
      // Filter out hidden projects first to skip P4 scanning
      const visibleItems = (statusJson || []).filter((item: any) => item.hidden !== true);
      
      const mappedTasks: TaskItem[] = await Promise.all(visibleItems.map(async (item: any, idx: number) => {
        const milestone = String(item.milestone || '').toLowerCase();
        const color = MILESTONE_COLORS[milestone] || TEAM_COLORS[idx % TEAM_COLORS.length];
        const leads = [item.etm_lead, item.int_lead, item.ckt_lead].filter(Boolean);
        const teamTags = resolveTeamsForLeads(leads);
        const primaryTeam = teamTags[0] || Object.keys(teamMap)[0] || 'Unassigned';
        
        // Determine if project is within visible status window:
        // current date between start and (end + 5 days grace period)
        const today = new Date();
        const startDate = new Date(item.start);
        const endDate = new Date(item.end);
        const endDateWithGrace = new Date(endDate);
        endDateWithGrace.setDate(endDateWithGrace.getDate() + 5);
        const isInProgress = today >= startDate && today <= endDateWithGrace;
        
        // Fetch cell status ONLY for projects in the visible status window to optimize performance
        let cellStatus: ProjectCellStatus | undefined = undefined;
        let progress = 0;
        
        if (item.rel && item.task && isInProgress) {
          try {
            console.log(`[Gantt] Fetching live cell status from p4 for IN PROGRESS project: ${item.task}/${item.rel}...`);
            
            // First, fetch config to get final_lib_path and cutoff_date
            const configRes = await fetch(`/api/project-status/config?project=${encodeURIComponent(item.task)}&subproject=${encodeURIComponent(item.rel)}`);
            let finalLibPath = '';
            let cutoffDate = '';
            
            if (configRes.ok) {
              const configResult = await configRes.json();
              if (configResult.config) {
                finalLibPath = configResult.config.final_lib_path || '';
                cutoffDate = configResult.config.cutoff_date || '';
                console.log(`[Gantt] ===== CONFIG FROM P4 =====`);
                console.log(`[Gantt] final_lib_path: "${finalLibPath}"`);
                console.log(`[Gantt] cutoff_date: "${cutoffDate}"`);
                console.log(`[Gantt] ===============================`);
              }
            }
            
            // Build URL with config params
            // Use refreshFromP4 parameter to force download from P4
            let url = `/api/project-status?project=${encodeURIComponent(item.task)}&subproject=${encodeURIComponent(item.rel)}&refresh=${refreshFromP4}`;
            if (finalLibPath) {
              url += `&final_lib_path=${encodeURIComponent(finalLibPath)}`;
            }
            if (cutoffDate) {
              url += `&cutoff_date=${encodeURIComponent(cutoffDate)}`;
            }
            
            // Fetch live data from p4 (same endpoint as project status page)
            const statusRes = await fetch(url);
            
            if (statusRes.ok) {
              const statusResult = await statusRes.json();
              console.log(`[Gantt] ✓ Loaded live data from p4 for ${item.task}/${item.rel}`);
              
              // statusResult has {data: [...], columns: {...}, project_status: {...}}
              const cells = statusResult.data;
              
              if (cells && Array.isArray(cells)) {
                console.log(`[Gantt] Successfully got ${cells.length} cells from p4`);
                
                // Split by tool type
                const sisCells = cells.filter((c: any) => c.tool && c.tool.toLowerCase() === 'sis');
                const ntCells = cells.filter((c: any) => c.tool && c.tool.toLowerCase() === 'nt');
                
                // Helper functions matching project_status.js semantics
                const isCheck = (val: any) => (val || '').toString().trim() === '✓';
                const checkField = (val: any) => {
                  const v = (val || '').toString().trim();
                  return v === '✓' || v.toLowerCase() === 'skip';
                };

                // For debugging logs (legacy, cell-based)
                const sisCompleted = sisCells.filter((c: any) => isCheck(c.tmqa) && isCheck(c.final_status));
                
                // Log incomplete SIS cells with reasons
                const sisIncomplete = sisCells.filter((c: any) => !(c.tmqa === '✓' && c.final_status === '✓'));
                if (sisIncomplete.length > 0) {
                  console.log(`[Gantt] ===== SIS INCOMPLETE CELLS (${sisIncomplete.length}/${sisCells.length}) =====`);
                  sisIncomplete.forEach((c: any) => {
                    const reasons = [];
                    if (c.tmqa !== '✓') reasons.push(`TMQA=${c.tmqa || 'empty'}`);
                    if (c.final_status !== '✓') reasons.push(`Final=${c.final_status || 'empty'}`);
                    console.log(`  ✗ ${c.ckt_macros}: ${reasons.join(', ')}`);
                  });
                }
                
                // NT: complete when all 5 fields are ✓ or 'skip' (legacy, cell-based)
                const ntCompleted = ntCells.filter((c: any) => 
                  checkField(c.tmqa) && 
                  checkField(c.final_status) && 
                  checkField(c.tmqc_spice_vs_nt) && 
                  checkField(c.tmqc_spice_vs_spice) && 
                  checkField(c.equalization)
                );
                
                // Log incomplete NT cells with reasons
                const ntIncomplete = ntCells.filter((c: any) => !(
                  checkField(c.tmqa) && 
                  checkField(c.final_status) && 
                  checkField(c.tmqc_spice_vs_nt) && 
                  checkField(c.tmqc_spice_vs_spice) && 
                  checkField(c.equalization)
                ));
                if (ntIncomplete.length > 0) {
                  console.log(`[Gantt] ===== NT INCOMPLETE CELLS (${ntIncomplete.length}/${ntCells.length}) =====`);
                  ntIncomplete.forEach((c: any) => {
                    const reasons = [];
                    if (!checkField(c.tmqa)) reasons.push(`TMQA=${c.tmqa || 'empty'}`);
                    if (!checkField(c.final_status)) reasons.push(`Final=${c.final_status || 'empty'}`);
                    if (!checkField(c.tmqc_spice_vs_nt)) reasons.push(`vsNT=${c.tmqc_spice_vs_nt || 'empty'}`);
                    if (!checkField(c.tmqc_spice_vs_spice)) reasons.push(`vsSpice=${c.tmqc_spice_vs_spice || 'empty'}`);
                    if (!checkField(c.equalization)) reasons.push(`Eq=${c.equalization || 'empty'}`);
                    console.log(`  ✗ ${c.ckt_macros}: ${reasons.join(', ')}`);
                  });
                }
                
                // INT: complete when ALL JIRA statuses are 'Done', 'Completed', or 'Skip'
                // COMMENTED OUT - Not needed currently
                // const intCompleted = ntCells.filter((c: any) => {
                //   const statusVal = (c.status || '').toString().trim();
                //   if (!statusVal) return false;
                //   const statuses = statusVal.split(/\n|,/).map((s: string) => s.trim()).filter(Boolean);
                //   if (statuses.length === 0) return false;
                //   return statuses.every((status: string) => {
                //     const lower = status.toLowerCase();
                //     return lower === 'done' || lower === 'completed' || lower === 'skip';
                //   });
                // });
                
                // Log incomplete INT cells with reasons
                // COMMENTED OUT - Not needed currently
                // const intIncomplete = ntCells.filter((c: any) => {
                //   const statusVal = (c.status || '').toString().trim();
                //   if (!statusVal) return true;
                //   const statuses = statusVal.split(/\n|,/).map((s: string) => s.trim()).filter(Boolean);
                //   if (statuses.length === 0) return true;
                //   return !statuses.every((status: string) => {
                //     const lower = status.toLowerCase();
                //     return lower === 'done' || lower === 'completed' || lower === 'skip';
                //   });
                // });
                // if (intIncomplete.length > 0) {
                //   console.log(`[Gantt] ===== INT INCOMPLETE CELLS (${intIncomplete.length}/${ntCells.length}) =====`);
                //   intIncomplete.forEach((c: any) => {
                //     const statusVal = (c.status || '').toString().trim();
                //     if (!statusVal) {
                //       console.log(`  ✗ ${c.ckt_macros}: Status=empty`);
                //     } else {
                //       const statuses = statusVal.split(/\n|,/).map((s: string) => s.trim()).filter(Boolean);
                //       const badStatuses = statuses.filter((s: string) => {
                //         const lower = s.toLowerCase();
                //         return !(lower === 'done' || lower === 'completed' || lower === 'skip');
                //       });
                //       console.log(`  ✗ ${c.ckt_macros}: Status=[${badStatuses.join(', ')}] (not Done/Completed/Skip)`);
                //     }
                //   });
                // }
                
                // Item-based completion (requested behavior)
                // SIS items: TMQA + Final Status per SIS cell
                const sisTotalItems = sisCells.length * 2;
                const sisCompletedItems = sisCells.reduce((acc: number, c: any) => {
                  return acc + (isCheck(c.tmqa) ? 1 : 0) + (isCheck(c.final_status) ? 1 : 0);
                }, 0);
                const sisPct = sisTotalItems > 0 ? (sisCompletedItems / sisTotalItems) * 100 : 0;

                // NT items: TMQA + Final + vsNT + vsSpice + Eq per NT cell
                const ntChecks: Array<{ key: string; label: string }> = [
                  { key: 'tmqa', label: 'TMQA' },
                  { key: 'final_status', label: 'Final' },
                  { key: 'tmqc_spice_vs_nt', label: 'vsNT' },
                  { key: 'tmqc_spice_vs_spice', label: 'vsSpice' },
                  { key: 'equalization', label: 'Eq' },
                ];
                const ntTotalItems = ntCells.length * ntChecks.length;
                const ntCompletedItems = ntCells.reduce((acc: number, c: any) => {
                  return acc + ntChecks.reduce((innerAcc, chk) => {
                    return innerAcc + (checkField(c[chk.key]) ? 1 : 0);
                  }, 0);
                }, 0);
                const ntPct = ntTotalItems > 0 ? (ntCompletedItems / ntTotalItems) * 100 : 0;

                const totalItems = sisTotalItems + ntTotalItems;
                const overallCompletion = totalItems > 0 ? ((sisCompletedItems + ntCompletedItems) / totalItems) * 100 : 0;
                
                cellStatus = {
                  project: item.task,
                  subproject: item.rel,
                  sis: {
                    total: sisTotalItems,
                    completed: sisCompletedItems
                  },
                  nt: {
                    total: ntTotalItems,
                    completed: ntCompletedItems
                  },
                  int: {
                    total: 0,  // INT commented out
                    completed: 0
                  },
                  overall_completion: overallCompletion
                };
                
                progress = overallCompletion;
                
                console.log(`[Gantt] Cell status for ${item.task}/${item.rel}:`, cellStatus);
                console.log(`[Gantt]   SIS items: ${sisCompletedItems}/${sisTotalItems} = ${sisPct.toFixed(1)}%`);
                console.log(`[Gantt]   NT items: ${ntCompletedItems}/${ntTotalItems} = ${ntPct.toFixed(1)}%`);
                // console.log(`[Gantt]   INT: ${intCompleted.length}/${ntCells.length} = ${intPct.toFixed(1)}%`);
                console.log(`[Gantt]   Overall: ${progress.toFixed(1)}%`);
              } else {
                console.warn(`[Gantt] Unexpected data structure from p4 for ${item.task}/${item.rel}`);
              }
            } else {
              console.warn(`[Gantt] Failed to fetch from p4 for ${item.task}/${item.rel}: ${statusRes.status} ${statusRes.statusText}`);
            }
          } catch (err) {
            console.error(`[Gantt] Error fetching cell status for ${item.task}/${item.rel}:`, err);
          }
        } else {
          if (!item.rel || !item.task) {
            console.log(`[Gantt] Skipping cell status for ${item.task} (no rel or task)`);
          } else if (!isInProgress) {
            console.log(`[Gantt] Skipping cell status for ${item.task}/${item.rel} (outside status window: start to end+5d)`);
          }
        }
        
        return {
          id: `${item.task}-${item.milestone}`,
          name: String(item.task || ''),
          startDate: new Date(item.start),
          endDate: new Date(item.end),
          progress,
          team: primaryTeam,
          teamTags,
          assignees: leads,
          color,
          milestone: String(item.milestone || ''),
          baseName: String(item.task || ''),
          rel: typeof item.rel === 'string' ? item.rel : undefined,
          note: typeof item.note === 'string' ? item.note : undefined,
          cellStatus,
        };
      }));

      setTeams(teamMap);
      setTasks(mappedTasks);
    } catch (err) {
      console.error('Failed to load Gantt data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  function resolveTeamsForLeads(leads: string[], teamMap: TeamMap): string[] {
    const tags = new Set<string>();
    for (const [teamName, teamInfo] of Object.entries(teamMap)) {
      const members = (teamInfo.members || []).map(m => String(m).trim());
      for (const lead of leads) {
        const name = String(lead || '').trim();
        if (!name) continue;
        if (members.includes(name)) tags.add(teamName);
      }
    }
    return Array.from(tags);
  }

  const onCreateTask = async () => {
    const base = newTaskName.trim();
    if (!base) { setAddOpen(false); return; }
    const leads = [etmLead, intLead, cktLead].filter(Boolean).map(s => s.trim());
    const teamTags = resolveTeamsForLeads(leads, teams);
    const primaryTeam = teamTags[0] || Object.keys(teams)[0] || 'Unassigned';
    const created: TaskItem[] = [];
    for (const m of milestoneKeys) {
      const { start, end, rel, note } = milestoneDates[m] || { start: '', end: '', rel: '', note: '' };
      if (!start || !end) continue;
      const startDate = new Date(start);
      const endDate = new Date(end);
      const color = MILESTONE_COLORS[m] || TEAM_COLORS[0];
      created.push({
        id: `${base}-${m}-${start}`,
        name: base,
        startDate,
        endDate,
        progress: 0,
        team: primaryTeam,
        teamTags,
        assignees: leads,
        color,
        milestone: m,
        baseName: base,
        rel: rel || undefined,
        note: note || undefined,
      });
    }
    if (created.length) {
      setTasks(prev => [...prev, ...created]);
      // Persist to backend (.cache/global_project_status.json)
      try {
        await fetch('/api/gantt/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task: base,
            etm_lead: etmLead,
            int_lead: intLead,
            ckt_lead: cktLead,
            milestones: {
              prelim: milestoneDates.prelim,
              prefinal: milestoneDates.prefinal,
              final: milestoneDates.final,
              swap_gds: milestoneDates.swap_gds,
            },
          }),
        });
      } catch (e) {
        console.error('Failed to persist task to backend', e);
      }
    }
    // reset and close
    setAddOpen(false);
    setNewTaskName('');
    setEtmLead('');
    setIntLead('');
    setCktLead('');
    setMilestoneDates({
      prelim: { start: '', end: '', rel: '', note: '' },
      prefinal: { start: '', end: '', rel: '', note: '' },
      final: { start: '', end: '', rel: '', note: '' },
      swap_gds: { start: '', end: '', rel: '', note: '' },
    });
  };

  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      const matchesSearch = task.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           task.assignees.some(assignee => assignee.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesTeam = selectedTeam === 'all' || task.team === selectedTeam || (task.teamTags || []).includes(selectedTeam);
      
      let matchesStatus = true;
      if (selectedStatus !== 'all') {
        const now = new Date();
        const isStarted = now >= task.startDate;
        const isNotEnded = now <= task.endDate;
        
        switch (selectedStatus) {
          case 'not-started':
            matchesStatus = now < task.startDate;
            break;
          case 'in-progress':
            matchesStatus = isStarted && isNotEnded;
            break;
          case 'completed':
            matchesStatus = now > task.endDate;
            break;
          case 'overdue':
            matchesStatus = now > task.endDate;
            break;
        }
      }
      
      return matchesSearch && matchesTeam && matchesStatus;
    });
  }, [searchTerm, selectedTeam, selectedStatus, tasks]);

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedTeam('all');
    setSelectedStatus('all');
  };

  const handleUpload = async () => {
    setUploading(true);
    try {
      const response = await fetch('/api/gantt/upload', { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        alert(`Successfully uploaded: ${result.uploaded.join(', ')}`);
      } else {
        alert(`Upload completed with errors:\n${result.errors.join('\n')}`);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Check console for details.');
    } finally {
      setUploading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('/api/gantt/refresh', { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        // Reload the data with refreshFromP4=true to force download individual project files from P4
        await loadData(true);
        alert(`Successfully refreshed: ${result.downloaded.join(', ')}`);
      } else {
        alert(`Refresh completed with errors:\n${result.errors.join('\n')}`);
      }
    } catch (error) {
      console.error('Refresh failed:', error);
      alert('Refresh failed. Check console for details.');
    } finally {
      setRefreshing(false);
    }
  };

  const handleTaskClick = (task: TaskItem) => {
    // Allow clicking in both edit and view mode
    setEditingTask(task);
    setEditStart(task.startDate.toISOString().split('T')[0]);
    setEditEnd(task.endDate.toISOString().split('T')[0]);
    setEditRel(task.rel || '');
    setEditEtm(task.assignees[0] || '');
    setEditInt(task.assignees[1] || '');
    setEditCkt(task.assignees[2] || '');
    setEditNote(task.note || '');
    setEditOpen(true);
  };

  const handleEditSave = async () => {
    if (!editingTask) return;
    
    const payload = {
      id: editingTask.id,
      task: editingTask.baseName || editingTask.name,
      milestone: editingTask.milestone,
      start: editStart,
      end: editEnd,
      rel: editRel,
      etm_lead: editEtm,
      int_lead: editInt,
      ckt_lead: editCkt,
      note: editNote,
    };
    console.log('[Gantt] Saving task with payload:', payload);
    
    try {
      const response = await fetch('/api/gantt/tasks/update', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      const result = await response.json();
      console.log('[Gantt] Update response:', result);
      if (result.success) {
        // Track what changed
        const changes: string[] = [];
        const taskLabel = `${payload.task}-${payload.milestone}`;
        
        if (editingTask.note !== editNote) {
          if (!editingTask.note && editNote) {
            changes.push(`Added note to ${taskLabel}: "${editNote}"`);
          } else if (editingTask.note && !editNote) {
            changes.push(`Removed note from ${taskLabel}`);
          } else {
            changes.push(`Updated note for ${taskLabel}: "${editNote}"`);
          }
        }
        if (editingTask.startDate.toISOString().split('T')[0] !== editStart) {
          changes.push(`Changed ${taskLabel} start date: ${editStart}`);
        }
        if (editingTask.endDate.toISOString().split('T')[0] !== editEnd) {
          changes.push(`Changed ${taskLabel} end date: ${editEnd}`);
        }
        if (editingTask.rel !== editRel) {
          changes.push(`Changed ${taskLabel} rel: ${editRel}`);
        }
        
        if (changes.length > 0) {
          setChangeLog(prev => [...prev, ...changes]);
        }
        
        // Update local state
        setTasks(prev => prev.map(t => 
          t.id === editingTask.id
            ? {
                ...t,
                startDate: new Date(editStart),
                endDate: new Date(editEnd),
                rel: editRel,
                note: editNote,
                assignees: [editEtm, editInt, editCkt].filter(Boolean),
              }
            : t
        ));
        alert('Task updated successfully!');
        setEditOpen(false);
      } else {
        alert(`Update failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Update failed:', error);
      alert('Update failed. Check console for details.');
    }
  };

  const handleEnterEditMode = async () => {
    // Clear change log when entering edit mode
    setChangeLog([]);
    // Refresh data first
    setRefreshing(true);
    try {
      const response = await fetch('/api/gantt/refresh', { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        // Reload the data with refreshFromP4=true to force download individual project files from P4
        await loadData(true);
      } else {
        alert(`Refresh completed with errors:\n${result.errors.join('\n')}`);
      }
    } catch (error) {
      console.error('Refresh failed:', error);
      alert('Refresh failed. Check console for details.');
    } finally {
      setRefreshing(false);
    }
    
    // Enter edit mode
    setEditMode(true);
  };

  const handleDone = async () => {
    // Upload to P4
    setUploading(true);
    try {
      const response = await fetch('/api/gantt/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          changes: changeLog,
        }),
      });
      const result = await response.json();
      if (result.success) {
        alert(`Successfully uploaded: ${result.uploaded.join(', ')}`);
        // Exit edit mode and clear change log
        setEditMode(false);
        setChangeLog([]);
      } else {
        alert(`Upload completed with errors:\n${result.errors.join('\n')}`);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Check console for details.');
    } finally {
      setUploading(false);
    }
  };

  // Get unique project names for manage projects modal (use allProjectNames from JSON)
  const uniqueProjects = useMemo(() => {
    return allProjectNames;
  }, [allProjectNames]);

  // Filter projects based on search term
  const filteredProjects = useMemo(() => {
    if (!projectSearchTerm.trim()) return uniqueProjects;
    const searchLower = projectSearchTerm.toLowerCase();
    return uniqueProjects.filter(p => p.toLowerCase().includes(searchLower));
  }, [uniqueProjects, projectSearchTerm]);

  const handleToggleProjectVisibility = (projectName: string) => {
    setHiddenProjects(prev => {
      const newSet = new Set(prev);
      if (newSet.has(projectName)) {
        newSet.delete(projectName);
      } else {
        newSet.add(projectName);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    // Show all projects (clear hidden set)
    setHiddenProjects(new Set());
  };

  const handleHideAll = () => {
    // Hide all projects
    setHiddenProjects(new Set(uniqueProjects));
  };

  const handleSaveProjectVisibility = async () => {
    try {
      const response = await fetch('/api/gantt/projects/visibility', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hiddenProjects: Array.from(hiddenProjects) }),
      });
      const result = await response.json();
      if (result.success) {
        alert('Project visibility saved successfully!');
        setManageProjectsOpen(false);
        // Reload data to apply visibility changes
        await loadData(false);
      } else {
        alert(`Failed to save: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to save project visibility:', error);
      alert('Failed to save. Check console for details.');
    }
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-6">
      {/* Loading overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-lg shadow-xl flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500"></div>
            <p className="text-lg font-semibold text-gray-900">Loading project data...</p>
          </div>
        </div>
      )}
      
      <div className="w-[80vw] mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">Cross-Team Collaboration</h1>
            <p className="text-muted-foreground">
              Track progress and coordinate across multiple teams
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            {!editMode ? (
              <Button onClick={handleEnterEditMode} disabled={refreshing}>
                {refreshing ? 'Loading...' : 'Edit'}
              </Button>
            ) : (
              <>
                <Button variant="outline" onClick={() => setManageProjectsOpen(true)}>
                  <Settings className="w-4 h-4 mr-2" />
                  Manage Projects
                </Button>
                <Button onClick={() => setAddOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Task
                </Button>
                <Button onClick={handleDone} disabled={uploading}>
                  <Upload className="w-4 h-4 mr-2" />
                  {uploading ? 'Uploading...' : 'Done'}
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Project Stats */}
        <ProjectStats tasks={tasks} teams={teams} />

        {/* Main Content */}
        <Tabs defaultValue="timeline" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="timeline" className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Timeline
            </TabsTrigger>
            <TabsTrigger value="teams" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Teams
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="timeline" className="space-y-6">
            <TaskFilters
              teams={teams}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              selectedTeam={selectedTeam}
              onTeamChange={setSelectedTeam}
              selectedStatus={selectedStatus}
              onStatusChange={setSelectedStatus}
              onClearFilters={clearFilters}
            />
            <GanttChart tasks={filteredTasks} teams={teams} onTaskClick={handleTaskClick} editMode={editMode} />
          </TabsContent>

          <TabsContent value="teams" className="space-y-6">
            <TeamOverview teams={teams} tasks={tasks} />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid gap-6">
              <ProjectStats tasks={tasks} teams={teams} />
              <div className="grid gap-4 md:grid-cols-2">
                {/* Team Performance Comparison */}
                <div className="col-span-full">
                  <TeamOverview teams={teams} tasks={tasks} />
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      
      {/* Add Task Modal */}
      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="w-[80vw] max-w-[1200px] sm:max-w-[1200px]">
          <DialogHeader>
            <DialogTitle>Add New Task</DialogTitle>
            <DialogDescription>
              Create a new base task and add milestone date ranges. All fields can be edited later.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="task">Task</Label>
                <Input id="task" value={newTaskName} onChange={e => setNewTaskName(e.target.value)} placeholder="e.g h218-ucie2-a64c-sf4a-12-ns" />
              </div>
              
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="etm">ETM Lead</Label>
                <Input id="etm" value={etmLead} onChange={e => setEtmLead(e.target.value)} placeholder="Judy" />
              </div>
              <div>
                <Label htmlFor="int">INT Lead</Label>
                <Input id="int" value={intLead} onChange={e => setIntLead(e.target.value)} placeholder="Frank" />
              </div>
              <div>
                <Label htmlFor="ckt">CKT Lead</Label>
                <Input id="ckt" value={cktLead} onChange={e => setCktLead(e.target.value)} placeholder="Bob" />
              </div>
            </div>

            <div className="space-y-3">
              <div className="font-medium">Milestones (start/end per phase)</div>
              {milestoneKeys.map((m) => (
                <div key={m} className="grid grid-cols-1 md:grid-cols-[120px_1fr_1fr_1fr_1fr] gap-3 items-start">
                  <div className="flex items-end h-full pb-2">
                    <span className="capitalize font-medium">{m.replace('_', ' ')}</span>
                  </div>
                  <div className="min-w-[150px]">
                    <Label htmlFor={`${m}-start`}>Start</Label>
                    <Input id={`${m}-start`} type="date" value={milestoneDates[m].start}
                      onChange={e => setMilestoneDates(prev => ({ ...prev, [m]: { ...prev[m], start: e.target.value } }))} />
                  </div>
                  <div className="min-w-[150px]">
                    <Label htmlFor={`${m}-end`}>End</Label>
                    <Input id={`${m}-end`} type="date" value={milestoneDates[m].end}
                      onChange={e => setMilestoneDates(prev => ({ ...prev, [m]: { ...prev[m], end: e.target.value } }))} />
                  </div>
                  <div className="min-w-[120px]">
                    <Label htmlFor={`${m}-rel`}>Rel</Label>
                    <Input id={`${m}-rel`} placeholder="e.g. 0.5_int" value={milestoneDates[m].rel}
                      onChange={e => setMilestoneDates(prev => ({ ...prev, [m]: { ...prev[m], rel: e.target.value } }))} />
                  </div>
                  <div className="min-w-[200px]">
                    <Label htmlFor={`${m}-note`}>Note</Label>
                    <Input id={`${m}-note`} placeholder="Optional note" value={milestoneDates[m].note}
                      onChange={e => setMilestoneDates(prev => ({ ...prev, [m]: { ...prev[m], note: e.target.value } }))} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button variant="secondary" onClick={() => setAddOpen(false)}>Cancel</Button>
            <Button onClick={onCreateTask}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Task Modal */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="w-[90vw] max-w-[1000px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editMode ? 'Edit Task' : 'View Task'}</DialogTitle>
            <DialogDescription>
              {editMode ? 'Modify' : 'View'} milestone details for {editingTask?.name} - {editingTask?.milestone}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Project Info and Link */}
            {editingTask && (
              <div className="p-4 bg-muted rounded-lg space-y-2">
                <div className="font-medium">Project Information</div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Task:</span> {editingTask.baseName || editingTask.name}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Milestone:</span> {editingTask.milestone}
                  </div>
                  {editingTask.rel && (
                    <div>
                      <span className="text-muted-foreground">Rel:</span> {editingTask.rel}
                    </div>
                  )}
                </div>
                {(() => {
                  const taskName = editingTask.baseName || editingTask.name;
                  const rel = editingTask.rel;
                  
                  if (taskName && rel) {
                    const handleProjectClick = () => {
                      // Set localStorage values: project = full task name, subproject = rel
                      localStorage.setItem('timing_selected_project', taskName);
                      localStorage.setItem('timing_selected_subproject', rel);
                      // Navigate to project status page
                      window.open('/project-status', '_blank');
                    };
                    
                    return (
                      <div className="pt-2">
                        <button 
                          onClick={handleProjectClick}
                          className="inline-flex items-center gap-2 text-sm text-primary hover:underline cursor-pointer bg-transparent border-0 p-0"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                            <polyline points="15 3 21 3 21 9"/>
                            <line x1="10" y1="14" x2="21" y2="3"/>
                          </svg>
                          Open Project Status ({taskName} / {rel})
                        </button>
                      </div>
                    );
                  }
                  return null;
                })()}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="edit-etm">ETM Lead</Label>
                <Input id="edit-etm" value={editEtm} onChange={e => setEditEtm(e.target.value)} disabled={!editMode} />
              </div>
              <div>
                <Label htmlFor="edit-int">INT Lead</Label>
                <Input id="edit-int" value={editInt} onChange={e => setEditInt(e.target.value)} disabled={!editMode} />
              </div>
              <div>
                <Label htmlFor="edit-ckt">CKT Lead</Label>
                <Input id="edit-ckt" value={editCkt} onChange={e => setEditCkt(e.target.value)} disabled={!editMode} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-[120px_1fr_1fr_1fr] gap-3 items-start">
              <div className="flex items-end h-full pb-2">
                <span className="capitalize font-medium">{editingTask?.milestone?.replace('_', ' ')}</span>
              </div>
              <div className="min-w-[150px]">
                <Label htmlFor="edit-start">Start</Label>
                <Input id="edit-start" type="date" value={editStart} onChange={e => setEditStart(e.target.value)} disabled={!editMode} />
              </div>
              <div className="min-w-[150px]">
                <Label htmlFor="edit-end">End</Label>
                <Input id="edit-end" type="date" value={editEnd} onChange={e => setEditEnd(e.target.value)} disabled={!editMode} />
              </div>
              <div className="min-w-[120px]">
                <Label htmlFor="edit-rel">Rel</Label>
                <Input id="edit-rel" placeholder="e.g. 0.5_int" value={editRel} onChange={e => setEditRel(e.target.value)} disabled={!editMode} />
              </div>
            </div>

            <div>
              <Label htmlFor="edit-note">Note</Label>
              <textarea
                id="edit-note"
                className="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-y"
                placeholder="Add notes about this task..."
                value={editNote}
                onChange={e => setEditNote(e.target.value)}
                disabled={!editMode}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="secondary" onClick={() => setEditOpen(false)}>{editMode ? 'Cancel' : 'Close'}</Button>
            {editMode && <Button onClick={handleEditSave}>Save Changes</Button>}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Manage Projects Modal */}
      <Dialog open={manageProjectsOpen} onOpenChange={(open) => {
        setManageProjectsOpen(open);
        if (!open) setProjectSearchTerm(''); // Clear search when closing
      }}>
        <DialogContent className="w-[600px] max-w-[90vw] max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>Manage Projects</DialogTitle>
            <DialogDescription>
              Select which projects to show or hide. Hidden projects won't be displayed and won't be scanned from P4, improving load time.
            </DialogDescription>
          </DialogHeader>

          {/* Search and Quick Actions */}
          <div className="space-y-3 pb-2 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
              <Input
                placeholder="Search projects..."
                value={projectSearchTerm}
                onChange={(e) => setProjectSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleSelectAll}>
                Show All
              </Button>
              <Button variant="outline" size="sm" onClick={handleHideAll}>
                Hide All
              </Button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 py-4">
            {filteredProjects.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No projects found matching "{projectSearchTerm}"
              </div>
            ) : (
              filteredProjects.map((projectName) => (
                <div key={projectName} className="flex items-center space-x-3 p-2 hover:bg-muted rounded">
                  <Checkbox
                    id={`project-${projectName}`}
                    checked={!hiddenProjects.has(projectName)}
                    onCheckedChange={() => handleToggleProjectVisibility(projectName)}
                  />
                  <Label
                    htmlFor={`project-${projectName}`}
                    className="flex-1 cursor-pointer text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    {projectName}
                  </Label>
                  {hiddenProjects.has(projectName) && (
                    <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">Hidden</span>
                  )}
                </div>
              ))
            )}
          </div>

          <div className="border-t pt-4 flex justify-between items-center">
            <div className="text-sm text-muted-foreground">
              {uniqueProjects.length - hiddenProjects.size} of {uniqueProjects.length} projects visible
            </div>
            <DialogFooter className="gap-2">
              <Button variant="secondary" onClick={() => setManageProjectsOpen(false)}>Cancel</Button>
              <Button onClick={handleSaveProjectVisibility}>Save</Button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
      </div>
    </div>
  );
}