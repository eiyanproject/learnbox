function r = two_adders()
% Two handles from the same factory must not share a captured n.
  a = make_adder(1);
  b = make_adder(10);
  r = [a(10) b(10)];
end
