classdef table
% TABLE  A MATLAB-style table, for lessons running on Octave.
%
% A table holds columns of different types side by side, each with a name, all
% the same height. That is the difference from a matrix (one type, no names)
% and from a struct of arrays (nothing keeps the lengths in step). Importing
% and organising data with tables is a scored part of the MATLAB Associate
% exam, and Octave has no table at all.
%
% MAKING ONE
%   table(ages, names)
%   table(ages, names, 'VariableNames', {'Age', 'Name'})
%   readtable('people.csv')
%
% READING IT
%   height(t), width(t), size(t)
%   t.Age                     one variable, as its own array
%   t(1:3, :)                 a smaller TABLE
%   t(t.Age > 18, :)          logical row selection
%   t{1, 'Age'}               the CONTENTS of one cell
%   t.Properties.VariableNames
%
% CHANGING IT
%   t.Score = [...]           add or replace a variable
%   addvars, removevars, renamevars
%   sortrows(t, 'Age'), sortrows(t, 'Age', 'descend')
%   head(t, k), tail(t, k)
%   rmmissing(t), ismissing(t)
%   groupsummary(t, 'City', 'mean', 'Age')
%
% () AGAINST {} - the distinction the exam asks about
%   t(1, 'Age') gives a 1x1 TABLE. t{1, 'Age'} gives the NUMBER inside it.
%   Parentheses always keep the container; braces reach through it.
%
% WHERE THIS DIVERGES FROM MATLAB
%   1. numel() is not overloaded; use height, width or size. See string.m.
%   2. No RowNames, no per-variable Units or Description.
%   3. join/innerjoin/outerjoin, stack/unstack and pivot are not implemented.
%   4. summary() prints a plain listing rather than MATLAB's formatted block.

  properties (Access = private)
    vars = {};    % 1xN cell, one entry per variable
    names = {};   % 1xN cellstr, the variable names
  end

  methods

    function obj = table(varargin)
      if nargin == 0
        return;
      end

      % Trailing 'VariableNames', {...} is the only option supported.
      given = {};
      args = varargin;
      i = 1;
      while i <= numel(args)
        if (ischar(args{i}) || isa(args{i}, 'string')) && i < numel(args) ...
            && strcmpi(table.astext(args{i}), 'VariableNames')
          given = table.astextlist(args{i + 1});
          args(i:i + 1) = [];
        else
          i = i + 1;
        end
      end

      obj.vars = args(:)';
      if isempty(given)
        obj.names = arrayfun(@(k) sprintf('Var%d', k), 1:numel(obj.vars), ...
                             'UniformOutput', false);
      else
        if numel(given) ~= numel(obj.vars)
          error('table:nameCount', 'got %d names for %d variables', ...
                numel(given), numel(obj.vars));
        end
        obj.names = given(:)';
      end
      table.checknames(obj.names);

      % Every variable must be the same height, or the table is not a table.
      if ~isempty(obj.vars)
        % An explicit loop, not cellfun(@table.rowcount, ...): Octave refuses a
        % function HANDLE to a private static method, though it allows a direct
        % call to one.
        heights = zeros(1, numel(obj.vars));
        for k = 1:numel(obj.vars)
          heights(k) = table.rowcount(obj.vars{k});
        end
        if numel(unique(heights)) > 1
          error('table:heightMismatch', ...
                'variables have different heights: %s', mat2str(heights));
        end
      end
    end

    % ---------- shape ----------

    function n = height(obj)
      if isempty(obj.vars)
        n = 0;
      else
        n = table.rowcount(obj.vars{1});
      end
    end

    function n = width(obj), n = numel(obj.vars); end

    function s = size(obj, dim)
      s = [height(obj), width(obj)];
      if nargin > 1
        s = s(dim);
      end
    end

    function r = isempty(obj), r = height(obj) == 0 || width(obj) == 0; end

    function n = end(obj, k, total)
      if total == 1
        n = height(obj);
      elseif k == 1
        n = height(obj);
      else
        n = width(obj);
      end
    end

    % ---------- variables ----------

    function r = istablevar(obj, name)
      r = any(strcmp(table.astext(name), obj.names));
    end

    function obj = addvars(obj, col, varargin)
      name = sprintf('Var%d', numel(obj.vars) + 1);
      for i = 1:2:numel(varargin)
        if strcmpi(table.astext(varargin{i}), 'NewVariableNames')
          n = table.astextlist(varargin{i + 1});
          name = n{1};
        end
      end
      obj = setvar(obj, name, col);
    end

    function obj = removevars(obj, which)
      names_ = table.astextlist(which);
      keep = true(1, numel(obj.names));
      for i = 1:numel(names_)
        at = find(strcmp(names_{i}, obj.names), 1);
        if isempty(at)
          error('table:noSuchVariable', 'no variable named %s', names_{i});
        end
        keep(at) = false;
      end
      obj.vars = obj.vars(keep);
      obj.names = obj.names(keep);
    end

    function obj = renamevars(obj, oldnames, newnames)
      olds = table.astextlist(oldnames);
      news = table.astextlist(newnames);
      if numel(olds) ~= numel(news)
        error('table:nameCount', 'got %d new names for %d old ones', ...
              numel(news), numel(olds));
      end
      for i = 1:numel(olds)
        at = find(strcmp(olds{i}, obj.names), 1);
        if isempty(at)
          error('table:noSuchVariable', 'no variable named %s', olds{i});
        end
        obj.names{at} = news{i};
      end
      table.checknames(obj.names);
    end

    % ---------- rows ----------

    function obj = head(obj, k)
      if nargin < 2, k = 8; end
      obj = rowslice(obj, 1:min(k, height(obj)));
    end

    function obj = tail(obj, k)
      if nargin < 2, k = 8; end
      n = height(obj);
      obj = rowslice(obj, max(1, n - k + 1):n);
    end

    function [obj, idx] = sortrows(obj, byname, direction)
      if nargin < 2
        error('table:sortrows', 'say which variable to sort by');
      end
      if nargin < 3, direction = 'ascend'; end
      col = getvar(obj, table.astext(byname));
      key = table.sortkey(col);
      [~, idx] = sort(key);
      if strcmpi(direction, 'descend')
        idx = idx(end:-1:1);
      elseif ~strcmpi(direction, 'ascend')
        error('table:sortDirection', 'direction must be ascend or descend');
      end
      obj = rowslice(obj, idx);
    end

    function m = ismissing(obj)
      m = false(height(obj), width(obj));
      for j = 1:width(obj)
        m(:, j) = table.missingmask(obj.vars{j});
      end
    end

    function obj = rmmissing(obj)
      bad = any(ismissing(obj), 2);
      obj = rowslice(obj, find(~bad));
    end

    % ---------- grouping ----------

    function out = groupsummary(obj, groupname, method, dataname)
      g = table.astext(groupname);
      keycol = getvar(obj, g);
      keys = table.grouplabels(keycol);
      [uniq, ~, which] = unique(keys);
      uniq = uniq(:);

      counts = zeros(numel(uniq), 1);
      for i = 1:numel(uniq)
        counts(i) = sum(which == i);
      end

      if nargin < 3 || isempty(method) || strcmpi(method, 'count')
        out = table(uniq, counts, 'VariableNames', {g, 'GroupCount'});
        return;
      end
      if nargin < 4
        error('table:groupsummary', 'say which variable to summarise');
      end

      d = table.astext(dataname);
      data = getvar(obj, d);
      if ~isnumeric(data)
        error('table:groupsummary', ...
              '%s is a %s; only numeric variables can be summarised', d, class(data));
      end

      vals = zeros(numel(uniq), 1);
      for i = 1:numel(uniq)
        chunk = data(which == i);
        switch lower(method)
          case 'sum',    vals(i) = sum(chunk);
          case 'mean',   vals(i) = mean(chunk);
          case 'max',    vals(i) = max(chunk);
          case 'min',    vals(i) = min(chunk);
          case 'median', vals(i) = median(chunk);
          otherwise
            error('table:groupsummary', 'unknown method %s', method);
        end
      end
      out = table(uniq, counts, vals, 'VariableNames', ...
                  {g, 'GroupCount', sprintf('%s_%s', lower(method), d)});
    end

    % ---------- display ----------

    function summary(obj)
      fprintf('    %d rows, %d variables\n', height(obj), width(obj));
      for j = 1:width(obj)
        fprintf('      %-16s %s\n', obj.names{j}, class(obj.vars{j}));
      end
    end

    function disp(obj)
      fprintf('    %dx%d table\n', height(obj), width(obj));
      if width(obj) == 0
        return;
      end
      fprintf('    %s\n', strjoin(obj.names, '  '));
      show = min(height(obj), 10);
      for i = 1:show
        cells = cell(1, width(obj));
        for j = 1:width(obj)
          cells{j} = table.celltext(obj.vars{j}, i);
        end
        fprintf('    %s\n', strjoin(cells, '  '));
      end
      if height(obj) > show
        fprintf('    ... %d more rows\n', height(obj) - show);
      end
    end

    % ---------- indexing ----------

    function varargout = subsref(obj, s)
      switch s(1).type

        case '.'
          key = s(1).subs;
          if strcmp(key, 'Properties')
            % The braces matter: struct('VariableNames', obj.names) would build
            % a STRUCT ARRAY, one element per name.
            r = struct('VariableNames', {obj.names});
          elseif any(strcmp(key, obj.names))
            r = getvar(obj, key);
          else
            [varargout{1:max(nargout, 1)}] = builtin('subsref', obj, s);
            return;
          end

        case '()'
          r = parenindex(obj, s(1).subs);

        case '{}'
          sub = parenindex(obj, s(1).subs);
          if width(sub) ~= 1
            error('table:braceWidth', ...
                  'braces must pick exactly one variable, not %d', width(sub));
          end
          r = sub.vars{1};
          if table.rowcount(r) == 1
            r = table.rowsub(r, 1);
            if iscell(r) && isscalar(r)
              r = r{1};   % a single cell reached through braces is its contents
            end
          end

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
      if strcmp(s(1).type, '.') && numel(s) == 1
        key = s(1).subs;
        if strcmp(key, 'Properties')
          error('table:properties', ...
                'set variable names with renamevars, not through Properties');
        end
        if isempty(val) && ~ischar(val) && istablevar(obj, key)
          obj = removevars(obj, key);   % t.Var = [] removes it, as in MATLAB
          return;
        end
        obj = setvar(obj, key, val);
        return;
      end
      obj = builtin('subsasgn', obj, s, val);
    end

  end

  % ------------------------------------------------------------------
  methods (Access = private)

    function col = getvar(obj, name)
      at = find(strcmp(name, obj.names), 1);
      if isempty(at)
        error('table:noSuchVariable', 'no variable named %s', name);
      end
      col = obj.vars{at};
    end

    function obj = setvar(obj, name, col)
      if ~isempty(obj.vars) && table.rowcount(col) ~= height(obj)
        error('table:heightMismatch', ...
              '%s has %d rows, the table has %d', ...
              name, table.rowcount(col), height(obj));
      end
      table.checknames({name});
      at = find(strcmp(name, obj.names), 1);
      if isempty(at)
        obj.vars{end + 1} = col;
        obj.names{end + 1} = name;
      else
        obj.vars{at} = col;
      end
    end

    function obj = rowslice(obj, idx)
      for j = 1:numel(obj.vars)
        obj.vars{j} = table.rowsub(obj.vars{j}, idx);
      end
    end

    function out = parenindex(obj, subs)
      if numel(subs) == 1
        rows = subs{1};
        cols = 1:width(obj);
      elseif numel(subs) == 2
        rows = subs{1};
        cols = subs{2};
      else
        error('table:subscripts', 'a table takes one or two subscripts');
      end

      rows = table.rowindex(rows, height(obj));
      cols = colindex(obj, cols);

      out = table();
      out.names = obj.names(cols);
      out.vars = cell(1, numel(cols));
      for k = 1:numel(cols)
        out.vars{k} = table.rowsub(obj.vars{cols(k)}, rows);
      end
    end

    function idx = colindex(obj, cols)
      if ischar(cols) && strcmp(cols, ':')
        idx = 1:width(obj);
        return;
      end
      if isnumeric(cols)
        idx = cols;
        return;
      end
      if islogical(cols)
        idx = find(cols);
        return;
      end
      wanted = table.astextlist(cols);
      idx = zeros(1, numel(wanted));
      for i = 1:numel(wanted)
        at = find(strcmp(wanted{i}, obj.names), 1);
        if isempty(at)
          error('table:noSuchVariable', 'no variable named %s', wanted{i});
        end
        idx(i) = at;
      end
    end

  end

  % ------------------------------------------------------------------
  methods (Static, Access = private)

    function n = rowcount(col)
      if isa(col, 'string') || isa(col, 'categorical') || ...
         isa(col, 'datetime') || isa(col, 'duration')
        n = length(col);
      else
        n = size(col, 1);
      end
    end

    function sub = rowsub(col, idx)
      if isa(col, 'string') || isa(col, 'categorical') || ...
         isa(col, 'datetime') || isa(col, 'duration')
        sub = col(idx);
      else
        sub = col(idx, :);
      end
    end

    function idx = rowindex(rows, n)
      if ischar(rows) && strcmp(rows, ':')
        idx = 1:n;
      elseif islogical(rows)
        if numel(rows) ~= n
          error('table:rowMask', ...
                'a logical row mask has %d entries for %d rows', numel(rows), n);
        end
        idx = find(rows);
      else
        idx = rows;
      end
    end

    function t = astext(v)
      if isa(v, 'string')
        c = cellstr(v);
        t = c{1};
      elseif ischar(v)
        t = v;
      elseif iscellstr(v) && isscalar(v)
        t = v{1};
      else
        error('table:badName', 'expected a variable name, got a %s', class(v));
      end
    end

    function c = astextlist(v)
      if isa(v, 'string')
        c = cellstr(v);
      elseif ischar(v)
        c = {v};
      elseif iscellstr(v)
        c = v;
      else
        error('table:badName', 'expected variable names, got a %s', class(v));
      end
      c = c(:)';
    end

    function checknames(names)
      for i = 1:numel(names)
        n = names{i};
        if ~ischar(n) || isempty(n)
          error('table:badName', 'variable names must be non-empty text');
        end
        if ~isvarname(n)
          error('table:badName', ...
                '"%s" is not a valid variable name - it must start with a letter and hold only letters, digits and underscores', n);
        end
      end
      if numel(unique(names)) ~= numel(names)
        error('table:duplicateName', 'variable names must be unique');
      end
    end

    function key = sortkey(col)
      if isnumeric(col) || islogical(col)
        key = double(col(:));
      elseif isa(col, 'datetime') || isa(col, 'duration')
        key = zeros(length(col), 1);
        for i = 1:length(col)
          key(i) = table.scalarkey(col(i));
        end
      elseif isa(col, 'categorical') || isa(col, 'string')
        key = cellstr(col);
        key = key(:);
      elseif iscellstr(col)
        key = col(:);
      else
        error('table:sortType', 'cannot sort a %s', class(col));
      end
    end

    function v = scalarkey(one)
      if isa(one, 'datetime')
        v = datenum(year(one), month(one), day(one), ...
                    hour(one), minute(one), second(one));
      else
        v = days(one);
      end
    end

    function m = missingmask(col)
      n = table.rowcount(col);
      if isnumeric(col)
        m = any(isnan(col), 2);
      elseif isa(col, 'categorical')
        m = isundefined(col);
        m = m(:);
      elseif iscellstr(col)
        m = cellfun(@isempty, col(:));
      elseif isa(col, 'string')
        m = strlength(col)' == 0;
        m = m(:);
      else
        m = false(n, 1);
      end
      m = reshape(m, n, 1);
    end

    function labels = grouplabels(col)
      if isa(col, 'categorical') || isa(col, 'string')
        labels = cellstr(col);
      elseif iscellstr(col)
        labels = col;
      elseif isnumeric(col)
        labels = arrayfun(@num2str, col, 'UniformOutput', false);
      else
        error('table:groupType', 'cannot group by a %s', class(col));
      end
      labels = labels(:);
    end

    function s = celltext(col, i)
      if isnumeric(col) || islogical(col)
        s = num2str(col(i, 1));
      elseif iscellstr(col)
        s = col{i};
      elseif isa(col, 'string') || isa(col, 'categorical')
        c = cellstr(col);
        s = c{i};
      elseif isa(col, 'datetime') || isa(col, 'duration')
        s = char(col(i));
      else
        s = sprintf('<%s>', class(col));
      end
    end

  end
end
