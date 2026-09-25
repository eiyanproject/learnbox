function out = parse_dates(c)
% PARSE_DATES  A datetime array from a cell array of date text.
%
% The catch turns an internal parse message into this function's own error, so
% a caller can match on parse_dates:bad rather than on wording that might
% change. The original message is kept in the text, where a person can read it.
  try
    out = datetime(c);
  catch err
    error('parse_dates:bad', 'could not read the dates: %s', err.message);
  end
end
