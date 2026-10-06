function [avg, n] = valid_mean(v)
% VALID_MEAN  The mean of the elements that are not NaN, and how many there are.
  ok = v(~isnan(v));
  n = numel(ok);
  if n == 0
    avg = 0;
  else
    avg = sum(ok) / n;
  end
end
