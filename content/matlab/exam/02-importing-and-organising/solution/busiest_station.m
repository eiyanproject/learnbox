function name = busiest_station(t)
% BUSIEST_STATION  The Station with the most rows, as a char array.
  if height(t) == 0
    error('busiest_station:empty', 'no rows to count');
  end
  g = groupsummary(t, 'Station');
  [~, at] = max(g.GroupCount);
  name = char(g.Station(at));
end
