function t = load_typed(filename)
% LOAD_TYPED  Read the CSV, convert Day and Station, drop rows with gaps.
  t = readtable(filename);
  t.Day = datetime(t.Day);
  t.Station = categorical(t.Station);
  t = rmmissing(t);
end
