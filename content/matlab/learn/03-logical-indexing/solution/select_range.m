function out = select_range(v, lo, hi)
% SELECT_RANGE  The elements of v within [lo, hi], inclusive.
%
% & and not &&: both sides are arrays here, and && would demand a single
% true or false from each.
  out = v(v >= lo & v <= hi);
end
