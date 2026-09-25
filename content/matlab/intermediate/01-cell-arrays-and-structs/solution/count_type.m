function n = count_type(c, className)
% COUNT_TYPE  How many elements of the cell array c have that class.
%
% The braces inside the lambda matter: cellfun already hands the CONTENTS of
% each cell to the function, so class(x) is the class of the thing, not 'cell'.
  n = sum(cellfun(@(x) strcmp(class(x), className), c));
end
