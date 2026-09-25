function out = top_n(t, varName, n)
% TOP_N  The n rows with the largest varName, ordered largest first.
%
% Asking for more rows than there are is not an error - it is the ordinary
% case of a short table, and the answer is all of them.
  sorted = sortrows(t, varName, 'descend');
  take = min(n, height(sorted));
  out = sorted(1:take, :);
end
