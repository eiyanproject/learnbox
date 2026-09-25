function m = north_mean()
% north keeps rows 1 and 5 after cleaning: 12.5 and 14.5.
  g = average_by(load_clean('readings.csv'), 'Station', 'Reading');
  g = sortrows(g, 'Station');
  m = g.mean_Reading(1);
end
