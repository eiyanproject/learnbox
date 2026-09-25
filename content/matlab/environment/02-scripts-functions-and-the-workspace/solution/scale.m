function out = scale(v, factor)
% SCALE  Multiply every element of v by factor, which defaults to 2.
%
% MATLAB has no default-argument syntax, so nargin - the number of arguments
% actually passed - is how a default is expressed.
  if nargin < 2
    factor = 2;
  end
  out = v * factor;
end
