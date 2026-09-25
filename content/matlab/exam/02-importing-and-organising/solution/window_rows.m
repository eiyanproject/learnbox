function out = window_rows(t, lo, hi)
% WINDOW_ROWS  The rows whose Day falls within [lo, hi], inclusive.
%
% isbetween gives a logical column, and a logical column is a row subscript.
  out = t(isbetween(t.Day, lo, hi), :);
end
