function v = expand_runs(values, counts)
% EXPAND_RUNS  Each value repeated its count of times, as one row vector.
  if numel(values) ~= numel(counts)
    error('expand_runs:size', 'expected one count per value');
  end
  if isempty(values)
    v = zeros(1, 0);
    return;
  end
  v = repelem(values(:).', counts(:).');
  if isempty(v)
    v = zeros(1, 0);
  end
end
