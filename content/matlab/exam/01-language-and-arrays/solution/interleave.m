function out = interleave(a, b)
% INTERLEAVE  [a(1) b(1) a(2) b(2) ...] as a row.
%
% Stacking the two as rows and reading the result down its columns is the
% interleaving - reshape fills column by column, which is the whole trick.
  if numel(a) ~= numel(b)
    error('interleave:sizeMismatch', ...
          'lengths %d and %d do not match', numel(a), numel(b));
  end
  if isempty(a)
    out = [];
    return;
  end
  out = reshape([a(:).'; b(:).'], 1, []);
end
