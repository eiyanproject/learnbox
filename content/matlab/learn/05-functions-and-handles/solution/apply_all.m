function out = apply_all(f, v)
% APPLY_ALL  f applied to each element of v.
%
% arrayfun expects one scalar back per element and collects them. For plain
% arithmetic a vectorised expression would be clearer and faster; this exists
% for when the caller supplies the operation.
  out = arrayfun(f, v);
end
