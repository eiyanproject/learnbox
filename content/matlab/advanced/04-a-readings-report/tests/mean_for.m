function m = mean_for(station)
  g = daily_summary(load_readings('sensors.csv'));
  at = find(g.Station == station, 1);
  m = g.mean_Reading(at);
end
