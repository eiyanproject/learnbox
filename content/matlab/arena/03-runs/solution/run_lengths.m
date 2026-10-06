function [values, counts] = run_lengths(v)
% RUN_LENGTHS  The value and the length of each run of equal neighbours in v.
  if isempty(v)
    values = zeros(1, 0);
    counts = zeros(1, 0);
    return;
  end
  v = v(:).';
  % The last position of every run: wherever the next element differs, and
  % the end of the vector.
  last = [find(diff(v) ~= 0), numel(v)];
  values = v(last);
  counts = diff([0, last]);
end
