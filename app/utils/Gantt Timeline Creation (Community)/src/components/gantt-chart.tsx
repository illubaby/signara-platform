import { useMemo, useRef, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Tooltip, TooltipTrigger, TooltipContent } from './ui/tooltip';

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

interface Task {
  id: string;
  name: string;
  startDate: Date;
  endDate: Date;
  progress: number;
  team: string;
  teamTags?: string[];
  assignees: string[];
  color: string;
  dependencies?: string[];
  milestone?: string;
  baseName?: string;
  rel?: string;
  cellStatus?: ProjectCellStatus;
}

interface GanttChartProps {
  tasks: Task[];
  teams: { [key: string]: { name: string; color: string; members: string[] } };
  onTaskClick?: (task: Task) => void;
  editMode?: boolean;
}

export function GanttChart({ tasks, teams, onTaskClick, editMode = false }: GanttChartProps) {
  const startOfDay = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const DAY_MS = 1000 * 60 * 60 * 24;
  const DAY_WIDTH = 28; // px per day

  // Dynamic window based on task dates (no artificial 2-month cap), with a small buffer
  const { minDate, maxDate, totalDays } = useMemo(() => {
    if (!tasks.length) {
      const today = startOfDay(new Date());
      const end = new Date(today);
      end.setDate(end.getDate() + 30);
      const total = Math.ceil((end.getTime() - today.getTime()) / DAY_MS);
      return { minDate: today, maxDate: end, totalDays: total };
    }
    const dates = tasks.flatMap(task => [startOfDay(task.startDate), startOfDay(task.endDate)]);
    const rawMin = new Date(Math.min(...dates.map(d => d.getTime())));
    const rawMax = new Date(Math.max(...dates.map(d => d.getTime())));
    const start = new Date(rawMin);
    start.setDate(start.getDate() - 14); // 2-week buffer before earliest task
    const end = new Date(rawMax);
    end.setDate(end.getDate() + 30); // 1-month buffer after latest task
    const total = Math.ceil((end.getTime() - start.getTime()) / DAY_MS);
    return { minDate: start, maxDate: end, totalDays: total };
  }, [tasks]);

  const getTaskPosition = (task: Task) => {
    // Clamp to the visible window and compute offsets in whole days
    const s = startOfDay(task.startDate);
    const e = startOfDay(task.endDate);
    const visStart = new Date(Math.max(s.getTime(), minDate.getTime()));
    const visEnd = new Date(Math.min(e.getTime(), maxDate.getTime()));
    if (visEnd.getTime() < minDate.getTime() || visStart.getTime() > maxDate.getTime()) return null;

    const startOffsetDays = Math.round((visStart.getTime() - minDate.getTime()) / DAY_MS);
    const durationDays = Math.max(1, Math.round((visEnd.getTime() - visStart.getTime()) / DAY_MS) + 1); // inclusive days
    return {
      leftPx: startOffsetDays * DAY_WIDTH,
      widthPx: durationDays * DAY_WIDTH,
    };
  };

  const generateTimelineHeaders = () => {
    const headers: Date[] = [];
    const current = new Date(minDate);
    while (current <= maxDate) {
      headers.push(new Date(current));
      current.setDate(current.getDate() + 1); // Daily intervals
    }
    return headers;
  };

  const timelineHeaders = generateTimelineHeaders();

  // Month spans for header row (label + width covering days in month)
  const monthSpans = useMemo(() => {
    const spans: { label: string; days: number }[] = [];
    const windowStart = new Date(minDate);
    const windowEnd = new Date(maxDate);
    let cursor = new Date(windowStart.getFullYear(), windowStart.getMonth(), 1);
    while (cursor <= windowEnd) {
      const monthStart = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
      const monthEnd = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0);
      const clampStart = new Date(Math.max(monthStart.getTime(), windowStart.getTime()));
      const clampEnd = new Date(Math.min(monthEnd.getTime(), windowEnd.getTime()));
      const days = Math.max(1, Math.floor((clampEnd.getTime() - clampStart.getTime()) / DAY_MS) + 1);
      spans.push({
        label: clampStart.toLocaleString('en-US', { month: 'short', year: 'numeric' }),
        days,
      });
      cursor = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1);
    }
    return spans;
  }, [minDate, maxDate]);

  const grouped = useMemo(() => {
    const map = new Map<string, Task[]>();
    for (const t of tasks) {
      const key = t.baseName || t.name;
      const arr = map.get(key) || [];
      arr.push(t);
      map.set(key, arr);
    }
    return Array.from(map.entries()).map(([key, arr]) => ({ key, items: arr }));
  }, [tasks]);

  const leftPanelRef = useRef<HTMLDivElement>(null);
  const timelineHeaderRef = useRef<HTMLDivElement>(null);
  const rowsRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [todayLeftPx, setTodayLeftPx] = useState(0);

  const getDateRatio = (date: Date) => {
    const d = startOfDay(date);
    const offsetDays = Math.floor((d.getTime() - minDate.getTime()) / DAY_MS);
    const ratio = Math.max(0, Math.min(1, offsetDays / totalDays));
    return ratio;
  };

  // Scroll to today on initial load
  useEffect(() => {
    if (!scrollContainerRef.current) return;
    
    const today = startOfDay(new Date());
    const offsetDays = Math.round((today.getTime() - minDate.getTime()) / DAY_MS);
    const todayPosition = offsetDays * DAY_WIDTH;
    
    // Scroll so that today is visible with some context (scroll back 2 weeks from today)
    const twoWeeksInPx = 14 * DAY_WIDTH;
    const scrollTarget = Math.max(0, todayPosition - twoWeeksInPx);
    
    scrollContainerRef.current.scrollLeft = scrollTarget;
  }, [minDate, totalDays]);

  useEffect(() => {
    const updateTodayPos = () => {
      const leftWidth = leftPanelRef.current?.offsetWidth || 0;
      const today = startOfDay(new Date());
      const offsetDays = Math.round((today.getTime() - minDate.getTime()) / DAY_MS);
      setTodayLeftPx(leftWidth + offsetDays * DAY_WIDTH);
    };

    updateTodayPos();

    const onResize = () => updateTodayPos();
    window.addEventListener('resize', onResize);

    const observers: ResizeObserver[] = [];
    if (typeof ResizeObserver !== 'undefined') {
      const ro = new ResizeObserver(() => updateTodayPos());
      observers.push(ro);
      if (timelineHeaderRef.current) ro.observe(timelineHeaderRef.current);
      if (leftPanelRef.current) ro.observe(leftPanelRef.current);
    }

    return () => {
      window.removeEventListener('resize', onResize);
      observers.forEach(o => o.disconnect());
    };
  }, [minDate]);

  

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Project Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div ref={scrollContainerRef} className="overflow-x-auto">
          <div className="relative">
          {/* Timeline Header */}
          <div className="flex border-b pb-2 mb-4 min-w-[800px]">
            <div ref={leftPanelRef} className="w-80 shrink-0 sticky left-0 z-20 bg-background">
              <div className="font-medium">Task</div>
            </div>
            <div ref={timelineHeaderRef} className="relative" style={{ width: `${totalDays * DAY_WIDTH}px` }}>
              {/* Month/Year header row */}
              <div className="flex border-b">
                {monthSpans.map((m, idx) => (
                  <div
                    key={idx}
                    className="text-center text-xs font-medium flex items-center justify-center"
                    style={{ width: `${m.days * DAY_WIDTH}px` }}
                  >
                    {m.label}
                  </div>
                ))}
              </div>
              {/* Day-of-month header row */}
              <div className="flex">
                {timelineHeaders.map((date, index) => (
                  <div
                    key={index}
                    className={`text-center text-xs border-l flex items-center justify-center ${[0,6].includes(date.getDay()) ? 'bg-gray-200 font-semibold' : ''}`}
                    style={{ width: `${DAY_WIDTH}px` }}
                    title={date.toDateString()}
                  >
                    {date.getDate()}
                  </div>
                ))}
              </div>
              {/* Global Today Indicator across header + rows */}
              <div
                className="absolute top-0 bottom-0 w-[2px] bg-red-500/70 pointer-events-none"
                style={{ left: `${(todayLeftPx - (leftPanelRef.current?.offsetWidth || 0))}px` }}
              />
            </div>
          </div>

          {/* Task Rows */}
          <div ref={rowsRef} className="space-y-3 relative" style={{ minWidth: '800px', width: `${(leftPanelRef.current?.offsetWidth || 320) + totalDays * DAY_WIDTH}px` }}>
            {/* Weekend background overlay across all rows */}
            <div
              className="absolute top-0 bottom-0 pointer-events-none"
              style={{ left: `${leftPanelRef.current?.offsetWidth || 0}px`, right: 0 }}
            >
              <div className="flex h-full" style={{ width: `${totalDays * DAY_WIDTH}px` }}>
                {timelineHeaders.map((date, index) => (
                  <div
                    key={`wk-${index}`}
                    className={`${[0,6].includes(date.getDay()) ? 'bg-gray-100' : ''}`}
                    style={{ width: `${DAY_WIDTH}px` }}
                  />
                ))}
              </div>
            </div>
            {/* Global Today Indicator spanning rows (clipped to timeline area) */}
            <div
              className="absolute top-0 bottom-0 pointer-events-none"
              style={{ left: `${leftPanelRef.current?.offsetWidth || 0}px`, right: 0 }}
            >
              <div
                className="absolute top-0 bottom-0 w-[2px] bg-red-500/70"
                style={{ left: `${(todayLeftPx - (leftPanelRef.current?.offsetWidth || 0))}px` }}
              />
            </div>
            {grouped.map(({ key, items }) => {
              // Combine teams and assignees per row
              const teamTags = Array.from(new Set(items.flatMap(it => it.teamTags || [it.team])));
              const teamBadges = teamTags.map(t => teams[t]).filter(Boolean);
              const assignees = Array.from(new Set(items.flatMap(it => it.assignees)));

              return (
                <div key={key} className="flex items-center group">
                  {/* Task Info */}
                  <div className="w-80 shrink-0 pr-4 sticky left-0 z-20 bg-background">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="font-medium">{key}</div>
                        <div className="mt-1 space-y-1">
                          <div className="flex items-center gap-2">
                            {teamBadges.map((t, i) => (
                              <Badge
                                key={i}
                                variant="secondary"
                                style={{ backgroundColor: t.color + '20', color: t.color }}
                              >
                                {t.name}
                              </Badge>
                            ))}
                          </div>
                          {/* Commented out Avatar section to reduce complexity */}
                          {/* <div className="flex flex-wrap gap-1">
                            {assignees.slice(0, 3).map((assignee, index) => (
                              <Tooltip key={index}>
                                <TooltipTrigger asChild>
                                  <Avatar className="h-6 w-auto min-w-[4rem] border-2 border-background rounded-full">
                                    <AvatarFallback className="text-[10px] px-3 whitespace-nowrap">
                                      {assignee}
                                    </AvatarFallback>
                                  </Avatar>
                                </TooltipTrigger>
                                <TooltipContent>{assignee}</TooltipContent>
                              </Tooltip>
                            ))}
                            {assignees.length > 3 && (
                              <div className="w-6 h-6 rounded-full bg-muted border-2 border-background flex items-center justify-center text-xs">
                                +{assignees.length - 3}
                              </div>
                            )}
                          </div> */}
                        </div>
                      </div>
                      {/* Current milestone progress (0% if no milestone in status window: start to end+5d) */}
                      <div className="text-sm text-muted-foreground flex-shrink-0">
                        {(() => {
                          const today = startOfDay(new Date());
                          const current = items.find(it => {
                            const endWithGrace = startOfDay(it.endDate);
                            endWithGrace.setDate(endWithGrace.getDate() + 5);
                            return startOfDay(it.startDate) <= today && today <= endWithGrace;
                          });
                          return current ? Math.round(current.progress || 0) : 0;
                        })()}%
                      </div>
                    </div>
                  </div>

                  {/* Timeline Bars - multiple bars per row */}
                  <div className="relative h-8" style={{ width: `${totalDays * DAY_WIDTH}px` }}>
                    {items.map((it) => {
                      const pos = getTaskPosition(it);
                      if (!pos) return null;
                      return (
                        <Tooltip key={it.id}>
                          <TooltipTrigger asChild>
                            <div
                              className={`absolute inset-y-1 rounded transition-all duration-200 group-hover:scale-105 cursor-pointer hover:shadow-lg`}
                              style={{ left: `${pos.leftPx - 7}px`, width: `${pos.widthPx}px`, backgroundColor: it.color }}
                              onClick={() => onTaskClick?.(it)}
                            >
                              <div className="h-full bg-white/20 rounded" style={{ width: `${it.progress}%` }} />
                              <div className="absolute inset-0 flex items-center justify-center text-[10px] text-white/90 font-medium pointer-events-none">
                                {(it.milestone || '').toUpperCase()}
                              </div>
                            </div>
                          </TooltipTrigger>
                          <TooltipContent className="max-w-xs">
                            <div className="space-y-2">
                              <div className="font-semibold text-sm">{it.name} - {it.milestone?.toUpperCase()}</div>
                              <div className="text-xs text-muted-foreground">
                                {it.startDate.toLocaleDateString()} - {it.endDate.toLocaleDateString()}
                              </div>
                              {it.rel && (
                                <div className="text-xs font-mono bg-gray-100 text-gray-900 px-2 py-1 rounded border border-gray-300">
                                  Version: {it.rel}
                                </div>
                              )}
                              {it.cellStatus && (
                                <div className="space-y-1.5 pt-2 border-t border-gray-500">
                                  <div className="text-xs font-semibold text-white">Item Completion: {it.cellStatus.overall_completion.toFixed(2)}%</div>
                                  
                                  {it.cellStatus.sis.total > 0 && (
                                    <div className="text-xs">
                                      <span className="font-medium text-white">SiS:</span>
                                      <span className="ml-2 text-green-300 font-semibold">{it.cellStatus.sis.completed}/{it.cellStatus.sis.total}</span>
                                      <span className="ml-1 text-gray-300">
                                        ({it.cellStatus.sis.total > 0 ? ((it.cellStatus.sis.completed / it.cellStatus.sis.total) * 100).toFixed(2) : '0.00'}%)
                                      </span>
                                    </div>
                                  )}
                                  
                                  {it.cellStatus.nt.total > 0 && (
                                    <div className="text-xs">
                                      <span className="font-medium text-white">NT:</span>
                                      <span className="ml-2 text-green-300 font-semibold">{it.cellStatus.nt.completed}/{it.cellStatus.nt.total}</span>
                                      <span className="ml-1 text-gray-300">
                                        ({it.cellStatus.nt.total > 0 ? ((it.cellStatus.nt.completed / it.cellStatus.nt.total) * 100).toFixed(2) : '0.00'}%)
                                      </span>
                                    </div>
                                  )}
                                  
                                  {it.cellStatus.int.total > 0 && (
                                    <div className="text-xs">
                                      <span className="font-medium text-white">INT:</span>
                                      <span className="ml-2 text-green-300 font-semibold">{it.cellStatus.int.completed}/{it.cellStatus.int.total}</span>
                                      <span className="ml-1 text-gray-300">
                                        ({it.cellStatus.int.total > 0 ? ((it.cellStatus.int.completed / it.cellStatus.int.total) * 100).toFixed(2) : '0.00'}%)
                                      </span>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </TooltipContent>
                        </Tooltip>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}