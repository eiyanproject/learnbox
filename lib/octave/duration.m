classdef duration
% DURATION  A length of time, as MATLAB's duration type.
%
% This is what you get by subtracting one datetime from another. It is a
% quantity of time, not a point in time, and keeping the two apart is the whole
% reason the type exists: "3 days" and "3 January" are not the same kind of
% thing, and only one of them can sensibly be doubled.
%
% MAKING ONE
%   days(3), hours(2), minutes(90), seconds(45)    the usual way
%   duration(1.5)                                  1.5 days
%   duration(90, 'minutes')
%
% READING ONE BACK
%   days(d), hours(d), minutes(d), seconds(d)      as numbers
%
% SUPPORTED
%   + - between durations, unary minus, * and / by a number, abs
%   ==, ~=, <, >, <=, >=
%   sum, max, min, sort, length, size, end, isempty, indexing with ()
%
% WHERE THIS DIVERGES FROM MATLAB
%   numel() is not overloaded; use length or size. See string.m for why.
%   calendarDuration (calmonths, calyears) is not implemented - a calendar
%   month is not a fixed length of time and needs different machinery.

  properties (Access = private)
    d = 0;   % days; everything else is a conversion of this
  end

  methods

    function obj = duration(v, unit)
      if nargin == 0
        return;
      end
      if isa(v, 'duration')
        obj.d = v.d;
        return;
      end
      if ~isnumeric(v)
        error('duration:badInput', 'expected a number, got a %s', class(v));
      end
      if nargin < 2
        obj.d = v;
      else
        switch lower(unit)
          case 'days',    obj.d = v;
          case 'hours',   obj.d = v / 24;
          case 'minutes', obj.d = v / 1440;
          case 'seconds', obj.d = v / 86400;
          otherwise
            error('duration:badUnit', 'unknown unit %s', unit);
        end
      end
    end

    % ---------- reading it back ----------

    function r = days(obj),    r = obj.d;          end
    function r = hours(obj),   r = obj.d * 24;     end
    function r = minutes(obj), r = obj.d * 1440;   end
    function r = seconds(obj), r = obj.d * 86400;  end

    % ---------- arithmetic ----------

    function r = plus(a, b)
      % Octave dispatches on the left operand, so days(7) + aDatetime lands
      % here rather than in datetime/plus. Hand it back the other way round;
      % datetime is the type that knows what adding a length of time means.
      if isa(b, 'datetime')
        r = b + a;
        return;
      end
      r = duration(duration.num(a) + duration.num(b));
    end

    function r = minus(a, b)
      % A length of time minus a point in time is meaningless, and saying so
      % is more useful than silently treating the datetime as a number.
      if isa(b, 'datetime')
        error('duration:badOperand', ...
              'cannot subtract a datetime from a duration');
      end
      r = duration(duration.num(a) - duration.num(b));
    end

    function r = uminus(obj), r = duration(-obj.d); end
    function r = abs(obj),    r = duration(abs(obj.d)); end

    function r = mtimes(a, b)
      % One side must be a plain number: a duration times a duration would be
      % an area of time, which means nothing.
      if isa(a, 'duration') && isnumeric(b)
        r = duration(a.d * b);
      elseif isnumeric(a) && isa(b, 'duration')
        r = duration(a * b.d);
      else
        error('duration:badProduct', 'a duration can only be scaled by a number');
      end
    end

    function r = times(a, b), r = mtimes(a, b); end

    function r = rdivide(a, b)
      if isa(a, 'duration') && isnumeric(b)
        r = duration(a.d ./ b);
      elseif isa(a, 'duration') && isa(b, 'duration')
        r = a.d ./ b.d;     % a ratio, so a plain number
      else
        error('duration:badQuotient', 'cannot divide that way');
      end
    end

    function r = mrdivide(a, b), r = rdivide(a, b); end

    % ---------- comparison ----------

    function r = eq(a, b), r = duration.num(a) == duration.num(b); end
    function r = ne(a, b), r = duration.num(a) ~= duration.num(b); end
    function r = lt(a, b), r = duration.num(a) <  duration.num(b); end
    function r = gt(a, b), r = duration.num(a) >  duration.num(b); end
    function r = le(a, b), r = duration.num(a) <= duration.num(b); end
    function r = ge(a, b), r = duration.num(a) >= duration.num(b); end

    % ---------- reductions ----------

    function r = sum(obj),  r = duration(sum(obj.d(:))); end
    function r = max(obj),  r = duration(max(obj.d(:))); end
    function r = min(obj),  r = duration(min(obj.d(:))); end
    function r = mean(obj), r = duration(mean(obj.d(:))); end

    function [r, idx] = sort(obj, varargin)
      [vals, idx] = sort(obj.d, varargin{:});
      r = duration(vals);
    end

    % ---------- size ----------

    function n = length(obj), n = numel(obj.d); end
    function s = size(obj, varargin), s = size(obj.d, varargin{:}); end
    function r = isempty(obj), r = isempty(obj.d); end

    function n = end(obj, k, total)
      if total == 1
        n = numel(obj.d);
      else
        n = size(obj.d, k);
      end
    end

    % ---------- display ----------

    function r = char(obj)
      if isscalar(obj.d)
        r = duration.render(obj.d);
      else
        parts = cell(1, numel(obj.d));
        for i = 1:numel(obj.d)
          parts{i} = duration.render(obj.d(i));
        end
        r = char(parts{:});
      end
    end

    function disp(obj)
      if isscalar(obj.d)
        fprintf('    %s\n', duration.render(obj.d));
      else
        for i = 1:numel(obj.d)
          fprintf('    %s\n', duration.render(obj.d(i)));
        end
      end
    end

    % ---------- indexing ----------

    function varargout = subsref(obj, s)
      if strcmp(s(1).type, '()')
        r = duration(obj.d(s(1).subs{:}));
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

    function n = num(v)
      if isa(v, 'duration')
        n = v.d;
      elseif isnumeric(v)
        n = v;   % a bare number is taken as days, matching duration(v)
      else
        error('duration:badOperand', 'expected a duration or a number, got a %s', class(v));
      end
    end

    function s = render(oneday)
      neg = oneday < 0;
      v = abs(oneday);
      whole = floor(v);
      rest = (v - whole) * 86400;
      hh = floor(rest / 3600);
      mm = floor(mod(rest, 3600) / 60);
      ss = mod(rest, 60);
      if whole > 0
        s = sprintf('%d days %02d:%02d:%05.2f', whole, hh, mm, ss);
      else
        s = sprintf('%02d:%02d:%05.2f', hh, mm, ss);
      end
      if neg
        s = ['-' s];
      end
    end

  end
end
