function t = no_rows()
  t = load_typed('sensors.csv');
  t = t([], :);
end
