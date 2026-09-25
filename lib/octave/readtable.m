function t = readtable(filename, varargin)
% READTABLE  Read a delimited text file into a table.
%
%   t = readtable('people.csv')
%   t = readtable('people.tsv', 'Delimiter', '\t')
%   t = readtable('raw.csv', 'ReadVariableNames', false)
%
% A column whose every entry parses as a number becomes numeric, and an empty
% entry in such a column becomes NaN - which is what makes ismissing and
% rmmissing work on data that has just been imported. Every other column comes
% in as a cell array of character vectors.
%
% WHERE THIS DIVERGES FROM MATLAB
%   No quoted fields containing the delimiter, no type detection beyond
%   numeric against text, no 'TextType', no date parsing. A date column arrives
%   as text; call datetime() on it, which is the step the lessons want visible
%   anyway.

  delim = ',';
  hasnames = true;
  for i = 1:2:numel(varargin)
    switch lower(varargin{i})
      case 'delimiter'
        delim = varargin{i + 1};
        if strcmp(delim, '\t')
          delim = sprintf('\t');
        end
      case 'readvariablenames'
        hasnames = logical(varargin{i + 1});
      otherwise
        error('readtable:badOption', 'unknown option %s', varargin{i});
    end
  end

  if exist(filename, 'file') ~= 2
    error('readtable:noSuchFile', 'cannot find %s', filename);
  end

  raw = fileread(filename);
  raw = strrep(raw, sprintf('\r\n'), sprintf('\n'));
  lines = strsplit(raw, sprintf('\n'));
  lines = lines(~cellfun(@(s) isempty(strtrim(s)), lines));
  if isempty(lines)
    t = table();
    return;
  end

  % CollapseDelimiters is true by default in Octave, which would turn
  % "north,2026-01-02,,good" into THREE fields and shift every column after
  % the gap. An empty field is exactly what this reader has to preserve.
  rows = cellfun(@(s) strsplit(s, delim, 'CollapseDelimiters', false), ...
                 lines, 'UniformOutput', false);
  ncol = max(cellfun(@numel, rows));

  % A short row is padded rather than rejected: a trailing empty field is the
  % most common thing wrong with a hand-edited CSV, and it is recoverable.
  for i = 1:numel(rows)
    if numel(rows{i}) < ncol
      rows{i}(end + 1:ncol) = {''};
    end
  end

  if hasnames
    names = cellfun(@strtrim, rows{1}, 'UniformOutput', false);
    names = readtable_fixnames(names);
    body = rows(2:end);
  else
    names = arrayfun(@(k) sprintf('Var%d', k), 1:ncol, 'UniformOutput', false);
    body = rows;
  end

  nrow = numel(body);
  vars = cell(1, ncol);
  for j = 1:ncol
    column = cell(nrow, 1);
    for i = 1:nrow
      column{i} = strtrim(body{i}{j});
    end
    vars{j} = readtable_convert(column);
  end

  t = table(vars{:}, 'VariableNames', names);
end

function out = readtable_convert(column)
% Numeric only when every non-empty entry is a number; an empty entry in an
% otherwise numeric column becomes NaN so the missing-data functions can see it.
  nums = zeros(numel(column), 1);
  allnumeric = true;
  for i = 1:numel(column)
    if isempty(column{i})
      nums(i) = NaN;
      continue;
    end
    v = str2double(column{i});
    if isnan(v)
      allnumeric = false;
      break;
    end
    nums(i) = v;
  end
  if allnumeric && ~isempty(column)
    out = nums;
  else
    out = column;
  end
end

function names = readtable_fixnames(names)
% A header cell that is not a valid identifier would make t.Name impossible, so
% it is repaired the way MATLAB repairs it rather than rejected.
  for i = 1:numel(names)
    n = regexprep(names{i}, '[^A-Za-z0-9_]', '_');
    if isempty(n) || ~isletter(n(1))
      n = ['Var' n];
    end
    names{i} = n;
  end
  for i = 1:numel(names)
    dupes = find(strcmp(names{i}, names));
    if numel(dupes) > 1
      for k = 2:numel(dupes)
        names{dupes(k)} = sprintf('%s_%d', names{dupes(k)}, k);
      end
    end
  end
end
