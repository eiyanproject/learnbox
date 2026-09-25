function out = normalise(v)
% NORMALISE  v scaled to the range [0, 1].
%
% A constant vector has no range, so the general formula is 0/0 and would give
% NaN. All-zeros is a decision, not an accident, and it keeps the output the
% same size and type as every other input.
  if isempty(v)
    out = v;
    return;
  end
  lo = min(v);
  hi = max(v);
  if hi == lo
    out = zeros(size(v));
    return;
  end
  out = (v - lo) / (hi - lo);
end
