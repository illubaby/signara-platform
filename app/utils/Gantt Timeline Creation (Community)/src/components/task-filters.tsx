import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Search, Filter, X } from 'lucide-react';

interface Team {
  name: string;
  color: string;
  members: string[];
}

interface TaskFiltersProps {
  teams: { [key: string]: Team };
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedTeam: string;
  onTeamChange: (value: string) => void;
  selectedStatus: string;
  onStatusChange: (value: string) => void;
  onClearFilters: () => void;
}

export function TaskFilters({
  teams,
  searchTerm,
  onSearchChange,
  selectedTeam,
  onTeamChange,
  selectedStatus,
  onStatusChange,
  onClearFilters
}: TaskFiltersProps) {
  const hasActiveFilters = searchTerm || selectedTeam !== 'all' || selectedStatus !== 'all';

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Team Filter */}
          <Select value={selectedTeam} onValueChange={onTeamChange}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by team" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Teams</SelectItem>
              {Object.entries(teams).map(([teamId, team]) => (
                <SelectItem key={teamId} value={teamId}>
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: team.color }}
                    />
                    {team.name}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Status Filter */}
          <Select value={selectedStatus} onValueChange={onStatusChange}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="not-started">Not Started</SelectItem>
              <SelectItem value="in-progress">In Progress</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="overdue">Overdue</SelectItem>
            </SelectContent>
          </Select>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <Button 
              variant="outline" 
              onClick={onClearFilters}
              className="shrink-0"
            >
              <X className="w-4 h-4 mr-2" />
              Clear
            </Button>
          )}
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Active filters:</span>
            
            {searchTerm && (
              <Badge variant="secondary">
                Search: "{searchTerm}"
              </Badge>
            )}
            
            {selectedTeam !== 'all' && (
              <Badge variant="secondary">
                Team: {teams[selectedTeam]?.name}
              </Badge>
            )}
            
            {selectedStatus !== 'all' && (
              <Badge variant="secondary">
                Status: {selectedStatus.replace('-', ' ')}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}