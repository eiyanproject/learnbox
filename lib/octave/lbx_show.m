function out = lbx_show(v)
% LBX_SHOW  A short, readable rendering of a value for a failure message.
% Deliberately truncated: a failed comparison against a 1000x1000 matrix should
% say what shape it was, not print it.
  if ischar(v)
    out = sprintf("\"%s\"", v);
  elseif islogical(v) && isscalar(v)
    if v, out = "true"; else, out = "false"; end
  elseif isnumeric(v) || islogical(v)
    if isempty(v)
      out = sprintf("%s empty", mat2str(size(v)));
    elseif numel(v) > 12
      out = sprintf("%s %s", class(v), mat2str(size(v)));
    else
      out = mat2str(v, 6);
    end
  elseif iscell(v)
    out = sprintf("cell %s", mat2str(size(v)));
  elseif isstruct(v)
    out = sprintf("struct with fields: %s", strjoin(fieldnames(v)', ", "));
  else
    out = sprintf("<%s>", class(v));
  end
end
