function t = is_symmetric(M)
% IS_SYMMETRIC  True when M equals its transpose.
%
% isequal rather than M == M.', because == gives a matrix of comparisons and
% `if` on that is true only when every entry is - which is nearly right and
% fails differently for an empty matrix.
  t = size(M, 1) == size(M, 2) && isequal(M, M.');
end
