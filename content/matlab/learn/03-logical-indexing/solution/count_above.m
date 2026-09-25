function n = count_above(v, t)
% COUNT_ABOVE  How many elements of v exceed t.
%
% Summing the mask counts it, because true adds as 1. No loop, no find.
  n = sum(v > t);
end
