function t = load_readings(filename)
% LOAD_READINGS  Read the CSV, convert the columns, drop rows with gaps.
%
% Convert before cleaning: a gap that arrived as NaN is already visible to
% ismissing, and converting afterwards would mean cleaning a table whose
% columns do not yet mean what they say.
  t = readtable(filename);
  t.Day = datetime(t.Day);
  t.Station = categorical(t.Station);
  t = rmmissing(t);
end
