function out = normalise_name(s)
% NORMALISE_NAME  Trimmed, lower case, with internal whitespace collapsed.
%
% strtrim before the regexprep: collapsing first would turn the leading run of
% whitespace into one leading space rather than removing it.
  out = regexprep(strtrim(s), '\s+', ' ');
  out = lower(out);
end
