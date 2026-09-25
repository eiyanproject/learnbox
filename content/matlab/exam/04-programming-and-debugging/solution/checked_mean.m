function m = checked_mean(v)
% CHECKED_MEAN  The mean of v, after checking it.
%
% In order, with a different identifier each time: an empty input, a
% non-numeric one and one holding NaN are three different mistakes, and a
% caller that can only tell them apart by reading the message is stuck.
  if isempty(v)
    error('checked_mean:empty', 'nothing to average');
  end
  if ~isnumeric(v)
    error('checked_mean:notNumeric', 'expected numbers, got a %s', class(v));
  end
  if any(isnan(v(:)))
    error('checked_mean:hasMissing', '%d value(s) are NaN', sum(isnan(v(:))));
  end
  m = mean(v(:));
end
