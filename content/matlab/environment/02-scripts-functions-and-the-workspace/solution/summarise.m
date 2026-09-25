function [mn, mx, avg] = summarise(v)
% SUMMARISE  The smallest, largest and mean of v.
%
% The empty case throws rather than returning something invented: there is no
% smallest value in an empty collection, and NaN would let the mistake travel.
  if isempty(v)
    error('summarise:empty', 'no values to summarise');
  end
  mn = min(v);
  mx = max(v);
  avg = mean(v);
end
