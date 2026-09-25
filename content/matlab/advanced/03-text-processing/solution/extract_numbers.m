function out = extract_numbers(s)
% EXTRACT_NUMBERS  Every number appearing in the text, as a numeric array.
%
% The pattern allows a leading minus and an optional decimal part. 'match'
% gives the matching TEXT, so each piece still has to be converted.
  found = regexp(s, '-?\d+(\.\d+)?', 'match');
  if isempty(found)
    out = [];
    return;
  end
  out = cellfun(@str2double, found);
end
