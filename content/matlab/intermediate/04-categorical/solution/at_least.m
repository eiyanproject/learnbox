function mask = at_least(sizes, ref)
% AT_LEAST  A logical mask of the entries at ref or above.
%
% This only means anything because to_sizes built an ordinal categorical; on
% an unordered one >= is refused rather than silently comparing codes.
  mask = sizes >= ref;
end
