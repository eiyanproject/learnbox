function ok = validate_scores(v)
% VALIDATE_SCORES  True when v is a non-empty numeric vector of 0 to 100.
%
% A different identifier per failure, so a caller can tell them apart. One
% shared 'invalid' would force them back to reading the message.
  if isempty(v)
    error('validate_scores:empty', 'no scores given');
  end
  if ~isnumeric(v)
    error('validate_scores:notNumeric', 'scores must be numeric, got a %s', class(v));
  end
  bad = v < 0 | v > 100;
  if any(bad)
    error('validate_scores:outOfRange', ...
          '%d score(s) outside 0 to 100, first is %g', sum(bad), v(find(bad, 1)));
  end
  ok = true;
end
