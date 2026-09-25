function out = row_sums(M)
% ROW_SUMS  The total of each row, as a column.
%
% sum(M) would add down the COLUMNS - dimension 1 is the default. The 2 is the
% whole difference and is worth writing even when it is the default elsewhere.
  out = sum(M, 2);
end
