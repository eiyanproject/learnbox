function r = hours(v)
% HOURS  Make a duration of V hours.
%
% MATLAB uses one name for both directions: hours(3) builds a duration and
% hours(d) reads one back as a number. The reading direction is a method on
% the duration class, which wins the dispatch, so this file only ever sees
% numbers. It refuses a duration rather than calling itself, which would
% recurse forever if that dispatch ever changed.
  if isnumeric(v)
    r = duration(v / 24);
  elseif isa(v, 'duration')
    error('hours:dispatch', ...
          'a duration should have reached duration/hours; check the class is on the path');
  else
    error('hours:badInput', 'expected a number, got a %s', class(v));
  end
end
