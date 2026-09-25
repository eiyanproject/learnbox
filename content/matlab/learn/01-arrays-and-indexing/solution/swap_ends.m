function out = swap_ends(v)
% SWAP_ENDS  v with its first and last elements exchanged.
%
% A one-element vector is already correct, and the general code would happen to
% work, but saying so costs one line and removes the doubt.
  out = v;
  if numel(v) < 2
    return;
  end
  out(1) = v(end);
  out(end) = v(1);
end
