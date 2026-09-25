function s = describe_sign(n)
% DESCRIBE_SIGN  'negative', 'zero' or 'positive'.
%
% sign() collapses the number to -1, 0 or 1, which is exactly the set of cases
% - so switch has three branches and no arithmetic hidden in them.
  switch sign(n)
    case -1
      s = 'negative';
    case 0
      s = 'zero';
    otherwise
      s = 'positive';
  end
end
