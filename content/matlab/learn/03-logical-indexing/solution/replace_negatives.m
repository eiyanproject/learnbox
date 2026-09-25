function out = replace_negatives(v, r)
% REPLACE_NEGATIVES  v with every negative replaced by r.
%
% Copy first: MATLAB passes by value, but assigning into the input variable
% would still be a confusing thing to read.
  out = v;
  out(out < 0) = r;
end
