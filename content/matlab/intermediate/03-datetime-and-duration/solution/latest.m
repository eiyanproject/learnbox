function d = latest(dates)
% LATEST  The latest datetime in the array.
%
% Empty throws: there is no latest moment in an empty collection, and any
% invented answer would be a date that never happened.
  if isempty(dates)
    error('latest:empty', 'no dates to choose from');
  end
  d = max(dates);
end
