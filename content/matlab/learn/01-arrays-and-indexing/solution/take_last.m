function out = take_last(v, n)
% TAKE_LAST  The last n elements of v.
%
% end means the last index, so this needs no reference to numel.
  if n > numel(v)
    error('take_last:tooMany', 'asked for %d of %d elements', n, numel(v));
  end
  out = v(end - n + 1:end);
end
