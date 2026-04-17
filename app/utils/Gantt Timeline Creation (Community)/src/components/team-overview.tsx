import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Tooltip, TooltipTrigger, TooltipContent } from './ui/tooltip';
import { Progress } from './ui/progress';
import { Users, Clock, CheckCircle } from 'lucide-react';

interface Team {
  name: string;
  color: string;
  members: string[];
}

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
}

interface TeamOverviewProps {
  teams: { [key: string]: Team };
  tasks: Task[];
}

export function TeamOverview({ teams, tasks }: TeamOverviewProps) {
  const getTeamStats = (teamId: string) => {
    const teamTasks = tasks.filter(task => task.team === teamId || (task.teamTags || []).includes(teamId));
    const totalTasks = teamTasks.length;
    const completedTasks = teamTasks.filter(task => task.progress === 100).length;
    const avgProgress = teamTasks.reduce((sum, task) => sum + task.progress, 0) / totalTasks || 0;
    const activeTasks = teamTasks.filter(task => {
      const now = new Date();
      return task.startDate <= now && task.endDate >= now && task.progress < 100;
    }).length;

    return {
      totalTasks,
      completedTasks,
      avgProgress,
      activeTasks
    };
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {Object.entries(teams).map(([teamId, team]) => {
        const stats = getTeamStats(teamId);
        
        return (
          <Card key={teamId}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: team.color }}
                  />
                  {team.name}
                </CardTitle>
                <Badge variant="outline">
                  {team.members.length} members
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Team Members */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Users className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Team Members</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {team.members.map((member, index) => (
                    <Tooltip key={index}>
                      <TooltipTrigger asChild>
                        <Avatar className="h-6 w-auto min-w-[4rem] border-2 border-background rounded-full">
                          <AvatarFallback className="text-[10px] px-3 whitespace-nowrap">
                            {member}
                          </AvatarFallback>
                        </Avatar>
                      </TooltipTrigger>
                      <TooltipContent>{member}</TooltipContent>
                    </Tooltip>
                  ))}
                </div>
              </div>

              {/* Progress Overview */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Overall Progress</span>
                  <span className="text-sm text-muted-foreground">{Math.round(stats.avgProgress)}%</span>
                </div>
                <Progress value={stats.avgProgress} className="h-2" />
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="space-y-1">
                  <div className="flex items-center justify-center">
                    <Clock className="w-4 h-4 text-blue-500" />
                  </div>
                  <div className="text-lg font-medium">{stats.activeTasks}</div>
                  <div className="text-xs text-muted-foreground">Active</div>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                  <div className="text-lg font-medium">{stats.completedTasks}</div>
                  <div className="text-xs text-muted-foreground">Complete</div>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-center">
                    <Users className="w-4 h-4 text-purple-500" />
                  </div>
                  <div className="text-lg font-medium">{stats.totalTasks}</div>
                  <div className="text-xs text-muted-foreground">Total</div>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}