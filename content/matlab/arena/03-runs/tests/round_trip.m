function out = round_trip(v)
  [values, counts] = run_lengths(v);
  out = expand_runs(values, counts);
end
