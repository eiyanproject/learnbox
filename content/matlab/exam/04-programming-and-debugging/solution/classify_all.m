function out = classify_all(v)
% CLASSIFY_ALL  A cell array of 'negative', 'zero' or 'positive'.
%
% The cell is preallocated: growing it with out{end+1} would reallocate and
% copy on every iteration.
  out = cell(size(v));
  for i = 1:numel(v)
    if v(i) < 0
      out{i} = 'negative';
    elseif v(i) == 0
      out{i} = 'zero';
    else
      out{i} = 'positive';
    end
  end
end
