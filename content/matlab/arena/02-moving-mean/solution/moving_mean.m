function out = moving_mean(v, k)
% MOVING_MEAN  The mean of every full window of k consecutive elements of v.
  if ~isscalar(k) || k < 1 || k ~= fix(k) || k > numel(v)
    error('moving_mean:window', 'the window must be a whole number from 1 to %d', numel(v));
  end
  % The sum of a window is the difference of two running totals.
  c = cumsum([0, v(:).']);
  out = (c(k + 1:end) - c(1:end - k)) / k;
end
