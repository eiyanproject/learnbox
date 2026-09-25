function out = every_other(v)
% EVERY_OTHER  Elements 1, 3, 5 and so on.
%
% first:step:last - the step is the middle term, not the last.
  out = v(1:2:end);
end
