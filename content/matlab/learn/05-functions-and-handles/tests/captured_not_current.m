function r = captured_not_current()
% The handle keeps the value n had when it was created, not the value the
% variable holds later.
  n = 5;
  adder = make_adder(n);
  n = 100;
  r = adder(1);
end
