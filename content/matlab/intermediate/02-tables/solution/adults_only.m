function out = adults_only(t)
% ADULTS_ONLY  The rows where Age is 18 or more.
%
% A logical column as a row subscript. The comma and colon are not optional:
% t(mask) without them would be asking for variables, not rows.
  out = t(t.Age >= 18, :);
end
