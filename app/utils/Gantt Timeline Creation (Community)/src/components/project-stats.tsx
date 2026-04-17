import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Calendar, Users, Target, TrendingUp } from 'lucide-react';

interface Task {
  id: string;
  name: string;
  startDate: Date;
  endDate: Date;
  progress: number;
  team: string;
  assignees: string[];
  color: string;
}

interface Team {
  name: string;
  color: string;
  members: string[];
}

interface ProjectStatsProps {
  tasks: Task[];
  teams: { [key: string]: Team };
}

export function ProjectStats({ tasks, teams }: ProjectStatsProps) {
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.progress === 100).length;
  const overallProgress = tasks.reduce((sum, task) => sum + task.progress, 0) / totalTasks || 0;
  
  const now = new Date();
  const activeTasks = tasks.filter(task => 
    task.startDate <= now && task.endDate >= now && task.progress < 100
  ).length;
  
  const overdueTasks = tasks.filter(task => 
    task.endDate < now && task.progress < 100
  ).length;

  const totalTeamMembers = Object.values(teams).reduce((sum, team) => sum + team.members.length, 0);
  
  // Calculate project timeline
  const projectStart = tasks.length > 0 ? new Date(Math.min(...tasks.map(t => t.startDate.getTime()))) : new Date();
  const projectEnd = tasks.length > 0 ? new Date(Math.max(...tasks.map(t => t.endDate.getTime()))) : new Date();
  const totalDays = Math.ceil((projectEnd.getTime() - projectStart.getTime()) / (1000 * 60 * 60 * 24));
  const daysPassed = Math.ceil((now.getTime() - projectStart.getTime()) / (1000 * 60 * 60 * 24));
  const timeProgress = Math.max(0, Math.min(100, (daysPassed / totalDays) * 100));

  const stats = [
    {
      title: "Overall Progress",
      value: `${Math.round(overallProgress)}%`,
      description: `${completedTasks}/${totalTasks} tasks completed`,
      icon: Target,
      progress: overallProgress,
      color: "bg-blue-500"
    },
    {
      title: "Timeline Progress", 
      value: `${Math.round(timeProgress)}%`,
      description: `${daysPassed}/${totalDays} days elapsed`,
      icon: Calendar,
      progress: timeProgress,
      color: "bg-green-500"
    },
    {
      title: "Team Utilization",
      value: `${activeTasks}`,
      description: `Active tasks across ${Object.keys(teams).length} teams`,
      icon: Users,
      progress: (activeTasks / totalTeamMembers) * 100,
      color: "bg-purple-500"
    },
    {
      title: "Performance",
      value: overdueTasks === 0 ? "On Track" : `${overdueTasks} Overdue`,
      description: `${Math.round((completedTasks / totalTasks) * 100)}% completion rate`,
      icon: TrendingUp,
      progress: overdueTasks === 0 ? 100 : Math.max(0, 100 - (overdueTasks / totalTasks) * 100),
      color: overdueTasks === 0 ? "bg-green-500" : "bg-red-500"
    }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        
        return (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stat.description}
              </p>
              <div className="mt-3">
                <Progress 
                  value={stat.progress} 
                  className="h-2"
                />
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}