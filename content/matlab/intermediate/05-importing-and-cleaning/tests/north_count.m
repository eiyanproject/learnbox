function n = north_count()
  g = average_by(load_clean('readings.csv'), 'Station', 'Reading');
  g = sortrows(g, 'Station');
  n = g.GroupCount(1);
end
