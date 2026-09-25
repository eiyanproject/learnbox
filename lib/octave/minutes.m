function r = minutes(v)
% MINUTES  Make a duration of V minutes.
%
% MATLAB uses one name for both directions: minutes(3) builds a duration and
% minutes(d) reads one back as a number. The reading direction is a method on
% the duration class, which wins the dispatch, so this file only ever sees
% numbers. It refuses a duration rather than calling itself, which would
% recurse forever if that dispatch ever changed.
  if isnumeric(v)
    r = duration(v / 1440);
  elseif isa(v, 'duration')
    error('minutes:dispatch', ...
          'a duration should have reached duration/minutes; check the class is on the path');
  else
    error('minutes:badInput', 'expected a number, got a %s', class(v));
  end
end
