function out = pairwise_diff(v)
% PAIRWISE_DIFF  The gaps between neighbouring elements.
%
% One element shorter than v, because n points have n-1 gaps between them.
  out = diff(v);
end
