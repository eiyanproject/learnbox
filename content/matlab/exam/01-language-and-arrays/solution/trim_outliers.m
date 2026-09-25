function out = trim_outliers(v, k)
% TRIM_OUTLIERS  v without the elements more than k standard deviations from
% the mean. Exactly k away counts as inside.
%
% <= rather than <: a constant vector has std 0, so every element sits exactly
% on the boundary, and < would throw all of them away.
  if isempty(v)
    out = v;
    return;
  end
  keep = abs(v - mean(v)) <= k * std(v);
  out = v(keep);
end
