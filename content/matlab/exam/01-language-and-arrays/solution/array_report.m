function r = array_report(v)
% ARRAY_REPORT  A struct describing v: n, mn, mx, avg and kind.
  if isempty(v)
    error('array_report:empty', 'nothing to report on');
  end
  r.n = numel(v);
  r.mn = min(v(:));
  r.mx = max(v(:));
  r.avg = mean(v(:));
  r.kind = class(v);
end
