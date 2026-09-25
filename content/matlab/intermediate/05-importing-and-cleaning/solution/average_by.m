function out = average_by(t, groupVar, dataVar)
% AVERAGE_BY  The mean of dataVar for each value of groupVar.
%
% One row per group, carrying a GroupCount as well as the mean - the count is
% what tells you whether a mean is worth reading.
  out = groupsummary(t, groupVar, 'mean', dataVar);
end
