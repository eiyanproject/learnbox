function out = most_common(c)
% MOST_COMMON  The most frequent value of a cell array of char.
%
% countcats and categories come back in the same order, so the position of the
% largest count is the position of its name. Inferred categories are sorted, so
% max taking the first of a tie means ties go to the first alphabetically -
% which is at least a rule, rather than whatever order the data arrived in.
  if isempty(c)
    error('most_common:empty', 'no values to count');
  end
  cats = categorical(c);
  counts = countcats(cats);
  names = categories(cats);
  [~, at] = max(counts);
  out = names{at};
end
