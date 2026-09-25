function mask = in_window(dates, lo, hi)
% IN_WINDOW  A logical mask of the dates within [lo, hi], inclusive.
%
% isbetween rather than dates >= lo & dates <= hi: the same answer, but it
% says what is meant in one call.
  mask = isbetween(dates, lo, hi);
end
