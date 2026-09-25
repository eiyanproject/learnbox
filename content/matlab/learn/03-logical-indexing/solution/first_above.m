function idx = first_above(v, t)
% FIRST_ABOVE  The first position where v exceeds t, or [] when there is none.
%
% The 1 makes find stop at the first hit instead of scanning the rest, and an
% empty result is the honest answer to "where is it" when it is nowhere.
  idx = find(v > t, 1);
end
