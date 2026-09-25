classdef datetime
% DATETIME  A point in time, as MATLAB's datetime type.
%
% Octave has datenum and datestr, which are a number and a piece of text. This
% shim gives the type instead, which is the thing the MATLAB Associate exam
% cares about: a datetime knows it is a date, so subtracting two of them gives
% a duration rather than a bare number of days, and comparing them does not
% depend on remembering what the number meant.
%
% MAKING ONE
%   datetime(2026, 1, 2)
%   datetime(2026, 1, 2, 3, 4, 5)
%   datetime("2026-01-02")            also "2026-01-02 03:04:05"
%   datetime({"2026-01-02", ...})     an array
%   datetime("now")
%
% SUPPORTED
%   year, month, day, hour, minute, second
%   d2 - d1  -> duration;   d + days(7) -> datetime;   d - hours(2)
%   ==, ~=, <, >, <=, >=, sort, min, max, isbetween
%   char, string, datestr, disp
%   length, size, isempty, end, indexing with () and logicals
%
% WHERE THIS DIVERGES FROM MATLAB
%   1. numel() is not overloaded; use length or size. See string.m for why.
%   2. No TimeZone, no Format property, no calendarDuration (calmonths and
%      calyears). Display is Octave's datestr default, dd-mmm-yyyy HH:MM:SS.
%   3. Parsing accepts what Octave's datenum accepts, which is close to but not
%      identical with MATLAB's. Lessons use ISO yyyy-MM-dd, which both agree on.

  properties (Access = private)
    n = [];   % serial day number, as datenum
  end

  methods

    function obj = datetime(varargin)
      if nargin == 0
        obj.n = now();
        return;
      end

      first = varargin{1};

      % datetime("now")
      if (ischar(first) || isa(first, 'string')) && nargin == 1
        txt = datetime.astext(first);
        if isscalar(txt) && any(strcmpi(txt{1}, {'now', 'today'}))
          if strcmpi(txt{1}, 'today')
            obj.n = floor(now());
          else
            obj.n = now();
          end
          return;
        end
        obj.n = zeros(size(txt));
        for i = 1:numel(txt)
          obj.n(i) = datetime.parse(txt{i});
        end
        return;
      end

      if iscell(first) && nargin == 1
        txt = datetime.astext(first);
        obj.n = zeros(size(txt));
        for i = 1:numel(txt)
          obj.n(i) = datetime.parse(txt{i});
        end
        return;
      end

      if isa(first, 'datetime') && nargin == 1
        obj.n = first.n;
        return;
      end

      % datetime(y, m, d [, h, mi, s])
      if ~isnumeric(first)
        error('datetime:badInput', 'cannot make a datetime from a %s', class(first));
      end
      if nargin < 3
        error('datetime:badInput', ...
              'numeric form needs at least year, month and day');
      end
      parts = zeros(1, 6);
      parts(4:6) = 0;
      for i = 1:min(nargin, 6)
        parts(i) = varargin{i};
      end
      obj.n = datenum(parts(1), parts(2), parts(3), parts(4), parts(5), parts(6));
    end

    % ---------- components ----------

    function r = year(obj),   v = datevec(obj.n); r = reshape(v(:, 1), size(obj.n)); end
    function r = month(obj),  v = datevec(obj.n); r = reshape(v(:, 2), size(obj.n)); end
    function r = day(obj),    v = datevec(obj.n); r = reshape(v(:, 3), size(obj.n)); end
    function r = hour(obj),   v = datevec(obj.n); r = reshape(v(:, 4), size(obj.n)); end
    function r = minute(obj), v = datevec(obj.n); r = reshape(v(:, 5), size(obj.n)); end
    function r = second(obj), v = datevec(obj.n); r = reshape(v(:, 6), size(obj.n)); end

    % ---------- arithmetic ----------

    function r = minus(a, b)
      if isa(a, 'datetime') && isa(b, 'datetime')
        % Two points in time give a length of time, not a number.
        r = duration(a.n - b.n);
      elseif isa(a, 'datetime') && isa(b, 'duration')
        r = datetime.fromnum(a.n - days(b));
      else
        error('datetime:badOperand', ...
              'subtract a datetime or a duration from a datetime, not a %s', class(b));
      end
    end

    function r = plus(a, b)
      if isa(a, 'datetime') && isa(b, 'duration')
        r = datetime.fromnum(a.n + days(b));
      elseif isa(a, 'duration') && isa(b, 'datetime')
        r = datetime.fromnum(b.n + days(a));
      else
        error('datetime:badOperand', ...
              'only a duration can be added to a datetime, not a %s', class(b));
      end
    end

    % ---------- comparison ----------

    function r = eq(a, b), r = datetime.num(a) == datetime.num(b); end
    function r = ne(a, b), r = datetime.num(a) ~= datetime.num(b); end
    function r = lt(a, b), r = datetime.num(a) <  datetime.num(b); end
    function r = gt(a, b), r = datetime.num(a) >  datetime.num(b); end
    function r = le(a, b), r = datetime.num(a) <= datetime.num(b); end
    function r = ge(a, b), r = datetime.num(a) >= datetime.num(b); end

    function r = isbetween(obj, lo, hi)
      r = obj.n >= datetime.num(lo) & obj.n <= datetime.num(hi);
    end

    % ---------- reductions ----------

    function r = max(obj), r = datetime.fromnum(max(obj.n(:))); end
    function r = min(obj), r = datetime.fromnum(min(obj.n(:))); end

    function [r, idx] = sort(obj, varargin)
      [vals, idx] = sort(obj.n, varargin{:});
      r = datetime.fromnum(vals);
    end

    % ---------- size ----------

    function n = length(obj), n = numel(obj.n); end
    function s = size(obj, varargin), s = size(obj.n, varargin{:}); end
    function r = isempty(obj), r = isempty(obj.n); end

    function n = end(obj, k, total)
      if total == 1
        n = numel(obj.n);
      else
        n = size(obj.n, k);
      end
    end

    % ---------- text ----------

    function r = datestr(obj, varargin)
      r = datestr(obj.n, varargin{:});
    end

    function r = char(obj)
      r = datestr(obj.n);
    end

    function r = string(obj)
      if isscalar(obj.n)
        r = string(datestr(obj.n));
      else
        parts = cell(size(obj.n));
        for i = 1:numel(obj.n)
          parts{i} = datestr(obj.n(i));
        end
        r = string(parts);
      end
    end

    function disp(obj)
      if isscalar(obj.n)
        fprintf('    %s\n', datestr(obj.n));
      else
        for i = 1:numel(obj.n)
          fprintf('    %s\n', datestr(obj.n(i)));
        end
      end
    end

    % ---------- indexing ----------

    function varargout = subsref(obj, s)
      if strcmp(s(1).type, '()')
        r = datetime.fromnum(obj.n(s(1).subs{:}));
        if numel(s) > 1
          [varargout{1:max(nargout, 1)}] = subsref(r, s(2:end));
        else
          varargout{1} = r;
        end
      else
        [varargout{1:max(nargout, 1)}] = builtin('subsref', obj, s);
      end
    end

  end

  methods (Static, Access = private)

    function obj = fromnum(v)
      obj = datetime(1, 1, 1);
      obj.n = v;
    end

    function r = num(v)
      if isa(v, 'datetime')
        r = v.n;
      elseif ischar(v) || iscell(v) || isa(v, 'string')
        r = datetime(v).n;
      else
        error('datetime:badOperand', 'expected a datetime, got a %s', class(v));
      end
    end

    function t = astext(v)
      if isa(v, 'string')
        t = cellstr(v);
      elseif ischar(v)
        t = {v};
      elseif iscellstr(v)
        t = v;
      else
        error('datetime:badInput', 'expected text, got a %s', class(v));
      end
    end

    function n = parse(s)
      s = strtrim(s);
      % Try ISO first, explicitly: it is what the lessons use and what MATLAB
      % and Octave agree on. Fall back to datenum's own guessing.
      formats = {'yyyy-mm-dd HH:MM:SS', 'yyyy-mm-dd'};
      for i = 1:numel(formats)
        try
          n = datenum(s, formats{i});
          return;
        catch
          % try the next one
        end
      end
      try
        n = datenum(s);
      catch
        error('datetime:unparsed', 'cannot read "%s" as a date', s);
      end
    end

  end
end
