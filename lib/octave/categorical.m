classdef categorical
% CATEGORICAL  A MATLAB-style categorical array, for lessons running on Octave.
%
% A categorical stores each value as a small integer code into a shared list of
% category names. That is why it exists: a column of 100,000 city names becomes
% 100,000 codes plus one list, instead of 100,000 separate char arrays. It also
% makes grouping and counting exact, because the set of possible values is
% known rather than inferred from the data present.
%
% SUPPORTED
%   categorical(cellstr)                       categories inferred, sorted
%   categorical(cellstr, valueset)             categories fixed by you
%   categorical(cellstr, valueset, names)      and renamed
%   categorical(..., 'Ordinal', true)          comparable with < and >
%   categories, countcats, iscategory, summary
%   addcats, removecats, renamecats
%   ==, ~=  against text or another categorical;  <, > when ordinal
%   double (the codes), cellstr, char, isundefined
%   length, size, isempty, end, indexing with () and logicals
%
% WHERE THIS DIVERGES FROM MATLAB
%   1. numel() is not overloaded - Octave sizes subsref's output list from it,
%      and overloading breaks indexing. Use length or size.
%   2. A value not in the category set becomes <undefined>, as in MATLAB, but
%      the display is plain text rather than MATLAB's formatting.

  properties (Access = private)
    codes = [];      % 0 means undefined
    cats = {};       % category names, in order
    isord = false;
  end

  methods

    function obj = categorical(v, valueset, catnames, varargin)
      if nargin == 0
        return;
      end

      % 'Ordinal', true may follow any of the positional forms.
      ord = false;
      for i = 1:2:numel(varargin)
        if strcmpi(varargin{i}, 'Ordinal')
          ord = logical(varargin{i + 1});
        end
      end
      obj.isord = ord;

      values = categorical.astext(v);

      if nargin < 2 || isempty(valueset)
        % Inferred categories are sorted, which is what makes two categoricals
        % built from different samples of the same data line up.
        present = values(~cellfun(@isempty, values));
        obj.cats = unique(present);
        obj.cats = obj.cats(:)';
      else
        obj.cats = categorical.astext(valueset);
        obj.cats = obj.cats(:)';
        if numel(unique(obj.cats)) ~= numel(obj.cats)
          error('categorical:duplicateCategory', 'the value set repeats a category');
        end
      end

      if nargin >= 3 && ~isempty(catnames)
        newnames = categorical.astext(catnames);
        if numel(newnames) ~= numel(obj.cats)
          error('categorical:nameCount', ...
                'got %d names for %d categories', numel(newnames), numel(obj.cats));
        end
      end

      obj.codes = zeros(size(values));
      for i = 1:numel(values)
        hit = find(strcmp(values{i}, obj.cats), 1);
        if isempty(hit)
          obj.codes(i) = 0;   % <undefined>
        else
          obj.codes(i) = hit;
        end
      end

      if nargin >= 3 && ~isempty(catnames)
        obj.cats = categorical.astext(catnames);
        obj.cats = obj.cats(:)';
      end
    end

    % ---------- the category list ----------

    function r = categories(obj)
      r = obj.cats(:);
    end

    function n = countcats(obj)
      n = zeros(1, numel(obj.cats));
      for i = 1:numel(obj.cats)
        n(i) = sum(obj.codes(:) == i);
      end
    end

    function r = iscategory(obj, name)
      names = categorical.astext(name);
      r = false(size(names));
      for i = 1:numel(names)
        r(i) = any(strcmp(names{i}, obj.cats));
      end
    end

    function obj = addcats(obj, name)
      names = categorical.astext(name);
      for i = 1:numel(names)
        if ~any(strcmp(names{i}, obj.cats))
          obj.cats{end + 1} = names{i};
        end
      end
    end

    function obj = removecats(obj, name)
      if nargin < 2
        % Drop categories nothing uses - the point of removecats with no
        % argument in MATLAB.
        used = unique(obj.codes(obj.codes > 0));
        keep = false(1, numel(obj.cats));
        keep(used) = true;
      else
        names = categorical.astext(name);
        keep = ~ismember(obj.cats, names);
      end
      remap = zeros(1, numel(obj.cats));
      remap(keep) = 1:sum(keep);
      newcodes = obj.codes;
      for i = 1:numel(newcodes)
        if newcodes(i) > 0
          newcodes(i) = remap(newcodes(i));
        end
      end
      obj.codes = newcodes;
      obj.cats = obj.cats(keep);
    end

    function obj = renamecats(obj, oldnames, newnames)
      if nargin == 2
        newnames = categorical.astext(oldnames);
        if numel(newnames) ~= numel(obj.cats)
          error('categorical:nameCount', ...
                'got %d names for %d categories', numel(newnames), numel(obj.cats));
        end
        obj.cats = newnames(:)';
        return;
      end
      olds = categorical.astext(oldnames);
      news = categorical.astext(newnames);
      for i = 1:numel(olds)
        at = find(strcmp(olds{i}, obj.cats), 1);
        if isempty(at)
          error('categorical:noSuchCategory', 'no category named %s', olds{i});
        end
        obj.cats{at} = news{i};
      end
    end

    function summary(obj)
      counts = countcats(obj);
      for i = 1:numel(obj.cats)
        fprintf('    %-16s %d\n', obj.cats{i}, counts(i));
      end
      undef = sum(obj.codes(:) == 0);
      if undef > 0
        fprintf('    %-16s %d\n', '<undefined>', undef);
      end
    end

    % ---------- conversion and size ----------

    function r = double(obj), r = obj.codes; end
    function r = isundefined(obj), r = obj.codes == 0; end
    function n = length(obj), n = numel(obj.codes); end
    function s = size(obj, varargin), s = size(obj.codes, varargin{:}); end
    function r = isempty(obj), r = isempty(obj.codes); end
    function r = isordinal(obj), r = obj.isord; end

    function n = end(obj, k, total)
      if total == 1
        n = numel(obj.codes);
      else
        n = size(obj.codes, k);
      end
    end

    function r = cellstr(obj)
      r = cell(size(obj.codes));
      for i = 1:numel(obj.codes)
        if obj.codes(i) == 0
          r{i} = '<undefined>';
        else
          r{i} = obj.cats{obj.codes(i)};
        end
      end
    end

    function r = char(obj)
      c = cellstr(obj);
      if isscalar(c)
        r = c{1};
      else
        r = char(c{:});
      end
    end

    % ---------- comparison ----------

    function r = eq(a, b)
      [x, y] = categorical.astexts(a, b);
      r = cellfun(@strcmp, x, y);
    end

    function r = ne(a, b), r = ~eq(a, b); end

    function r = lt(a, b), r = categorical.order(a, b) < 0; end
    function r = gt(a, b), r = categorical.order(a, b) > 0; end
    function r = le(a, b), r = categorical.order(a, b) <= 0; end
    function r = ge(a, b), r = categorical.order(a, b) >= 0; end

    function r = ismember(obj, set)
      names = categorical.astext(set);
      mine = cellstr(obj);
      r = ismember(mine, names);
    end

    % ---------- display and indexing ----------

    function disp(obj)
      c = cellstr(obj);
      for i = 1:numel(c)
        fprintf('    %s\n', c{i});
      end
    end

    function varargout = subsref(obj, s)
      switch s(1).type
        case '()'
          r = obj;
          r.codes = obj.codes(s(1).subs{:});
        case '{}'
          error('categorical:braceIndex', ...
                'a categorical does not support {} indexing; use cellstr()');
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

  end

  methods (Static, Access = private)

    function t = astext(v)
      if isa(v, 'categorical')
        t = cellstr(v);
      elseif isa(v, 'string')
        t = cellstr(v);
      elseif ischar(v)
        if size(v, 1) > 1
          t = cell(size(v, 1), 1);
          for i = 1:size(v, 1)
            t{i} = deblank(v(i, :));
          end
        else
          t = {v};
        end
      elseif iscellstr(v)
        t = v;
      elseif isnumeric(v)
        t = cell(size(v));
        for i = 1:numel(v)
          t{i} = num2str(v(i));
        end
      else
        error('categorical:badInput', 'cannot make categories from a %s', class(v));
      end
    end

    function [x, y] = astexts(a, b)
      x = categorical.astext(a);
      y = categorical.astext(b);
      if isscalar(x) && ~isscalar(y)
        x = repmat(x, size(y));
      elseif isscalar(y) && ~isscalar(x)
        y = repmat(y, size(x));
      elseif ~isequal(size(x), size(y))
        error('categorical:sizeMismatch', 'sizes %s and %s do not match', ...
              mat2str(size(x)), mat2str(size(y)));
      end
    end

    function d = order(a, b)
      % Ordinal comparison goes by position in the category list, which is why
      % MATLAB refuses it unless the categorical was built as ordinal: for an
      % unordered one the position is an implementation detail, not a meaning.
      if isa(a, 'categorical')
        ref = a;
      else
        ref = b;
      end
      if ~ref.isord
        error('categorical:notOrdinal', ...
              'this categorical is not ordinal, so < and > have no meaning');
      end
      [x, y] = categorical.astexts(a, b);
      d = zeros(size(x));
      for i = 1:numel(x)
        pa = find(strcmp(x{i}, ref.cats), 1);
        pb = find(strcmp(y{i}, ref.cats), 1);
        if isempty(pa) || isempty(pb)
          error('categorical:noSuchCategory', 'comparing against a value outside the category set');
        end
        d(i) = pa - pb;
      end
    end

  end
end
