function out = initials(fullname)
% INITIALS  'ada lovelace' becomes 'A.L'.
%
% Empty input is its own case: strsplit('') gives one empty piece, and taking
% p(1) of it would be an index error rather than an empty answer.
  trimmed = strtrim(fullname);
  if isempty(trimmed)
    out = '';
    return;
  end
  parts = strsplit(trimmed);
  parts = parts(~cellfun(@isempty, parts));
  letters = cellfun(@(p) upper(p(1)), parts, 'UniformOutput', false);
  out = strjoin(letters, '.');
end
