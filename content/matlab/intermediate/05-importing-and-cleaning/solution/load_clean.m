function t = load_clean(filename)
% LOAD_CLEAN  Read a CSV and drop rows with anything missing.
%
% Dropping is the simplest answer and worth being explicit about: on a small
% table with scattered gaps it can remove most of the data, and the caller
% should be choosing it rather than inheriting it.
  t = rmmissing(readtable(filename));
end
