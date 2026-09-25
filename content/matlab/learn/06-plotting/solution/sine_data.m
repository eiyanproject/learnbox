function [x, y] = sine_data(n)
% SINE_DATA  n points over one full period of sine.
%
% linspace, not 0:step:2*pi - the count is what matters here, and linspace
% guarantees the endpoints land exactly on 0 and 2*pi.
  if n < 2
    error('sine_data:tooFew', 'need at least 2 points, got %d', n);
  end
  x = linspace(0, 2 * pi, n);
  y = sin(x);
end
