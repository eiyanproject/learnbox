function [ew, mp] = product_pair(A, B)
% PRODUCT_PAIR  The element-wise product and the matrix product of A and B.
%
% Both are legal for two square matrices of the same size, and they give
% different answers. That is the bug the dot exists to prevent.
  ew = A .* B;
  mp = A * B;
end
