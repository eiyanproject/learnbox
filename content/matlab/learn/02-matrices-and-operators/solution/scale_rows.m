function out = scale_rows(M, factors)
% SCALE_ROWS  Row i of M multiplied by factors(i).
%
% factors(:) forces a column, so broadcasting stretches it across the columns
% and scales rows. Passed a row vector instead, the same expression would scale
% COLUMNS - and would not complain.
  if numel(factors) ~= size(M, 1)
    error('scale_rows:sizeMismatch', ...
          'got %d factors for %d rows', numel(factors), size(M, 1));
  end
  out = M .* factors(:);
end
