function adder = make_adder(n)
% MAKE_ADDER  A handle that adds n to its argument.
%
% n is captured by VALUE when the handle is created, so the returned handle
% still has it after this function has returned and n has gone out of scope.
  adder = @(x) x + n;
end
