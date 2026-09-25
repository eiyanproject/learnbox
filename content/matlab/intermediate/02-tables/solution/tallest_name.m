function name = tallest_name(t)
% TALLEST_NAME  The Name of the tallest row, as a char array.
%
% The second output of max is the position, which is what indexes back into
% the other variable. Braces reach the value; parentheses would give a 1x1
% table instead.
  if height(t) == 0
    error('tallest_name:empty', 'no rows to choose from');
  end
  [~, at] = max(t.Height);
  name = t{at, 'Name'};
end
