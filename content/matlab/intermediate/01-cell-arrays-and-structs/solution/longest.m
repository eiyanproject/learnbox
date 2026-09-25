function out = longest(c)
% LONGEST  The longest char element of c, or '' when there are none.
%
% Ties go to the first, which is worth deciding rather than leaving to
% whichever comparison happens to run last.
  out = '';
  for i = 1:numel(c)
    if ischar(c{i}) && length(c{i}) > length(out)
      out = c{i};
    end
  end
end
