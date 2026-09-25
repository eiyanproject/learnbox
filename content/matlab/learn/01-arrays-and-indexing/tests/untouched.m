function v = untouched()
% MATLAB passes by value, so a function cannot change its caller's array.
  v = [1 2 3];
  swap_ends(v);
end
