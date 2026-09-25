function s = summary_stats(v)
% SUMMARY_STATS  A struct with avg, med, sd and rng.
%
% Both the mean and the median, because quoting one alone hides skew: a single
% large outlier moves the mean and leaves the median where it was.
  if isempty(v)
    error('summary_stats:empty', 'nothing to summarise');
  end
  s.avg = mean(v(:));
  s.med = median(v(:));
  s.sd = std(v(:));
  s.rng = max(v(:)) - min(v(:));
end
