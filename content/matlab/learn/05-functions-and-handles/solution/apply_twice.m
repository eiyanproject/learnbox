function out = apply_twice(f, x)
% APPLY_TWICE  f applied to x, twice.
%
% A handle is called exactly like a named function. Nothing here knows or
% cares what f actually is.
  out = f(f(x));
end
