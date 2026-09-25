function r = days(v)
% DAYS  Make a duration of V days.
%
% MATLAB uses one name for both directions: days(3) builds a duration and
% days(d) reads one back as a number. The reading direction is a method on
% the duration class, which wins the dispatch, so this file only ever sees
% numbers. It refuses a duration rather than calling itself, which would
% recurse forever if that dispatch ever changed.
  if isnumeric(v)
    r = duration(v / 1);
  elseif isa(v, 'duration')
    error('days:dispatch', ...
          'a duration should have reached duration/days; check the class is on the path');
  else
    error('days:badInput', 'expected a number, got a %s', class(v));
  end
end
