function r = seconds(v)
% SECONDS  Make a duration of V seconds.
%
% MATLAB uses one name for both directions: seconds(3) builds a duration and
% seconds(d) reads one back as a number. The reading direction is a method on
% the duration class, which wins the dispatch, so this file only ever sees
% numbers. It refuses a duration rather than calling itself, which would
% recurse forever if that dispatch ever changed.
  if isnumeric(v)
    r = duration(v / 86400);
  elseif isa(v, 'duration')
    error('seconds:dispatch', ...
          'a duration should have reached duration/seconds; check the class is on the path');
  else
    error('seconds:badInput', 'expected a number, got a %s', class(v));
  end
end
