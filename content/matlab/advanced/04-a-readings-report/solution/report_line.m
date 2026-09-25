function s = report_line(t)
% REPORT_LINE  A one-line summary of the readings.
%
% The empty case is decided before max is called: max of nothing throws, and
% "no readings" is a perfectly good thing for a report to say.
  if height(t) == 0
    s = 'no readings';
    return;
  end
  g = daily_summary(t);
  [~, at] = max(g.mean_Reading);
  best = g.Station(at);
  s = sprintf('%d readings from %d stations; highest mean %s at %.1f', ...
              height(t), height(g), char(best), g.mean_Reading(at));
end
