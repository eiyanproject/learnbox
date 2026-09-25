function [ok, value] = try_parse(text)
% TRY_PARSE  Parse text as a number, without throwing when it is not one.
%
% Text that is not a number is a normal thing to meet - it usually came from a
% person - so this reports rather than throws. Both outputs are assigned on
% every path, which is what makes the result safe to use unchecked.
  value = 0;
  ok = false;
  if ~ischar(text) && ~isa(text, 'string')
    return;
  end
  if isa(text, 'string')
    text = char(text);
  end
  parsed = str2double(strtrim(text));
  if isnan(parsed)
    return;
  end
  value = parsed;
  ok = true;
end
