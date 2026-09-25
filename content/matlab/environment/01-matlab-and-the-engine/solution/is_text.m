function t = is_text(v)
% IS_TEXT  True for a char array or a string.
%
% Two different types hold text, and code that accepts either has to say so.
% ischar is the char array; isa(v, 'string') is the string.
  t = ischar(v) || isa(v, 'string');
end
