classdef string
% STRING  A MATLAB-style string array, for lessons running on Octave.
%
% Octave 9 has no string class: "hi" there is a 1x2 char array, the same as
% 'hi'. This shim provides the type so the lessons can teach the distinction
% between text-as-characters and text-as-a-value, which the MATLAB Associate
% exam asks about directly.
%
% SUPPORTED
%   string(...)            from char, cellstr, numeric or another string
%   char, cellstr, double  conversions back out
%   strlength, length, size, isempty, end
%   + (concatenation), ==, ~=, <, >  (ordinal, elementwise)
%   contains, startsWith, endsWith
%   upper, lower, strtrim, replace, reverse
%   split, join, strcat, plus with numbers
%   indexing:  s(2), s(end), s(logical([...]))
%
% WHERE THIS DIVERGES FROM MATLAB - say so when a lesson relies on it
%   1. There is no string LITERAL. In MATLAB "hi" is a string and 'hi' is a
%      char array; in Octave both are char. Lessons must write string("hi")
%      explicitly. This is the one difference you cannot paper over.
%   2. numel() is not overloaded. Octave decides how many outputs to ask
%      subsref for by calling numel, so overloading it breaks every form of
%      indexing - and Octave ignores numArgumentsFromSubscript, which is how
%      MATLAB lets you have both. Use strlength, length or size instead.
%   3. No automatic display of the variable name on assignment without a
%      semicolon; disp works normally.

  properties (Access = private)
    c = {};   % cell array of char, shaped like the string array
  end

  methods

    function obj = string(v)
      if nargin == 0
        obj.c = {''};
        return;
      end
      if isa(v, 'string')
        obj.c = v.c;
      elseif ischar(v)
        % A char matrix becomes one string per row, as MATLAB does.
        if size(v, 1) > 1
          obj.c = cell(size(v, 1), 1);
          for i = 1:size(v, 1)
            obj.c{i} = deblank(v(i, :));
          end
        else
          obj.c = {v};
        end
      elseif iscell(v)
        if ~iscellstr(v)
          error('string:badInput', 'a cell array must contain only character vectors');
        end
        obj.c = v;
      elseif isnumeric(v) || islogical(v)
        obj.c = cell(size(v));
        for i = 1:numel(v)
          obj.c{i} = num2str(v(i));
        end
      else
        error('string:badInput', 'cannot make a string from a %s', class(v));
      end
    end

    % ---------- conversions ----------

    function r = char(obj)
      if isscalar(obj.c)
        r = obj.c{1};
      else
        r = char(obj.c{:});
      end
    end

    function r = cellstr(obj)
      r = obj.c;
    end

    function r = double(obj)
      r = zeros(size(obj.c));
      for i = 1:numel(obj.c)
        r(i) = str2double(obj.c{i});
      end
    end

    % ---------- size ----------
    % numel is deliberately absent; see the header.

    function n = strlength(obj)
      n = zeros(size(obj.c));
      for i = 1:numel(obj.c)
        n(i) = length(obj.c{i});
      end
    end

    function n = length(obj), n = numel(obj.c); end
    function s = size(obj, varargin), s = size(obj.c, varargin{:}); end
    function r = isempty(obj), r = isempty(obj.c); end
    function r = isscalar(obj), r = isscalar(obj.c); end
    function n = end(obj, k, total)
      % With one subscript, end means the last element in linear order, not
      % the last row. s(end) on a 1xN must be N.
      if total == 1
        n = numel(obj.c);
      else
        n = size(obj.c, k);
      end
    end
    function r = isstring(obj), r = true; end

    % ---------- comparison ----------

    function r = eq(a, b)
      [x, y] = string.pair(a, b);
      r = cellfun(@strcmp, x, y);
    end

    function r = ne(a, b), r = ~eq(a, b); end

    function r = lt(a, b)
      [x, y] = string.pair(a, b);
      r = cellfun(@(p, q) string.cmp(p, q) < 0, x, y);
    end

    function r = gt(a, b)
      [x, y] = string.pair(a, b);
      r = cellfun(@(p, q) string.cmp(p, q) > 0, x, y);
    end

    % ---------- text operations ----------

    function r = plus(a, b)
      [x, y] = string.pair(a, b);
      out = cell(size(x));
      for i = 1:numel(x)
        out{i} = [x{i} y{i}];
      end
      r = string(out);
    end

    function r = contains(obj, pat)
      p = string.text(pat);
      r = cellfun(@(s) ~isempty(strfind(s, p)), obj.c);
    end

    function r = startsWith(obj, pat)
      p = string.text(pat);
      r = cellfun(@(s) length(s) >= length(p) && strcmp(s(1:length(p)), p), obj.c);
    end

    function r = endsWith(obj, pat)
      p = string.text(pat);
      r = cellfun(@(s) length(s) >= length(p) && strcmp(s(end-length(p)+1:end), p), obj.c);
    end

    function r = upper(obj), r = string(cellfun(@upper, obj.c, 'UniformOutput', false)); end
    function r = lower(obj), r = string(cellfun(@lower, obj.c, 'UniformOutput', false)); end
    function r = strtrim(obj), r = string(cellfun(@strtrim, obj.c, 'UniformOutput', false)); end
    function r = reverse(obj), r = string(cellfun(@fliplr, obj.c, 'UniformOutput', false)); end

    function r = replace(obj, old, new)
      o = string.text(old);
      n = string.text(new);
      r = string(cellfun(@(s) strrep(s, o, n), obj.c, 'UniformOutput', false));
    end

    function r = split(obj, delim)
      if nargin < 2, delim = ' '; end
      d = string.text(delim);
      if ~isscalar(obj.c)
        error('string:split', 'split takes a single string, not an array');
      end
      parts = strsplit(obj.c{1}, d);
      r = string(parts(:));   % a column, as MATLAB returns
    end

    function r = join(obj, delim)
      if nargin < 2, delim = ' '; end
      d = string.text(delim);
      r = string(strjoin(obj.c(:)', d));
    end

    function r = strcat(varargin)
      r = varargin{1};
      for i = 2:numel(varargin)
        r = plus(r, varargin{i});
      end
    end

    % ---------- display ----------

    function disp(obj)
      if isscalar(obj.c)
        fprintf('    "%s"\n', obj.c{1});
      else
        for i = 1:numel(obj.c)
          fprintf('    "%s"\n', obj.c{i});
        end
      end
    end

    % ---------- indexing ----------

    function varargout = subsref(obj, s)
      switch s(1).type
        case '()'
          r = string(obj.c(s(1).subs{:}));
        case '{}'
          r = obj.c{s(1).subs{:}};
        otherwise
          [varargout{1:max(nargout, 1)}] = builtin('subsref', obj, s);
          return;
      end
      if numel(s) > 1
        [varargout{1:max(nargout, 1)}] = subsref(r, s(2:end));
      else
        varargout{1} = r;
      end
    end

    function obj = subsasgn(obj, s, val)
      if strcmp(s(1).type, '()')
        obj.c(s(1).subs{:}) = string(val).c;
      else
        obj = builtin('subsasgn', obj, s, val);
      end
    end

    function r = horzcat(varargin)
      parts = {};
      for i = 1:numel(varargin)
        parts = [parts, reshape(string(varargin{i}).c, 1, [])];
      end
      r = string(parts);
    end

    function r = vertcat(varargin)
      parts = {};
      for i = 1:numel(varargin)
        parts = [parts; reshape(string(varargin{i}).c, [], 1)];
      end
      r = string(parts);
    end

  end

  methods (Static, Access = private)

    function t = text(v)
      % Accept a shim string, a char vector or a 1x1 cellstr wherever a
      % pattern is wanted, so lessons can pass whichever they have.
      if isa(v, 'string')
        t = v.c{1};
      elseif ischar(v)
        t = v;
      elseif iscellstr(v) && isscalar(v)
        t = v{1};
      else
        error('string:badPattern', 'expected text, got a %s', class(v));
      end
    end

    function [x, y] = pair(a, b)
      % Bring both operands to cell arrays of char of a common shape, so the
      % elementwise operators can scalar-expand the way MATLAB's do.
      x = string(a).c;
      y = string(b).c;
      if isscalar(x) && ~isscalar(y)
        x = repmat(x, size(y));
      elseif isscalar(y) && ~isscalar(x)
        y = repmat(y, size(x));
      elseif ~isequal(size(x), size(y))
        error('string:sizeMismatch', 'sizes %s and %s do not match', ...
              mat2str(size(x)), mat2str(size(y)));
      end
    end

    function d = cmp(p, q)
      n = min(length(p), length(q));
      for i = 1:n
        if p(i) ~= q(i)
          d = double(p(i)) - double(q(i));
          return;
        end
      end
      d = length(p) - length(q);
    end

  end
end
