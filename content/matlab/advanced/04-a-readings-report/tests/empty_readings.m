function t = empty_readings()
  t = load_readings('sensors.csv');
  t = t([], :);
end
