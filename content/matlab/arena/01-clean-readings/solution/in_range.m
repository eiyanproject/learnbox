function out = in_range(v, lo, hi)
% IN_RANGE  The elements of v between lo and hi inclusive, in order.
  out = v(v >= lo & v <= hi);
end
