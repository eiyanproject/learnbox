function out = take_first(v, n)
% TAKE_FIRST  The first n elements of v.
%
% The check is explicit so the error says what went wrong. MATLAB's own index
% error would name a subscript, not the argument the caller passed.
  if n > numel(v)
    error('take_first:tooMany', 'asked for %d of %d elements', n, numel(v));
  end
  out = v(1:n);
end
