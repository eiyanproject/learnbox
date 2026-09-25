function n = count_runs(v)
% COUNT_RUNS  How many runs of equal consecutive values v has.
%
% A run ends wherever consecutive elements differ, so the number of boundaries
% is sum(diff(v) ~= 0) and the number of runs is one more. Empty is its own
% case: no elements means no runs, where the formula would say one.
  if isempty(v)
    n = 0;
    return;
  end
  n = sum(diff(v) ~= 0) + 1;
end
