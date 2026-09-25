function g = daily_summary(t)
% DAILY_SUMMARY  The mean Reading for each Station.
%
% The GroupCount comes back too, and it is the part that says whether a mean
% is worth reading: the mean of a single reading is that reading.
  g = groupsummary(t, 'Station', 'mean', 'Reading');
end
