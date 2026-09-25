function v = field_or(s, name, default)
% FIELD_OR  The named field of s, or default when it is absent.
%
% isfield asks first; s.(name) on a missing field is an error, not an empty.
  if isfield(s, name)
    v = s.(name);
  else
    v = default;
  end
end
