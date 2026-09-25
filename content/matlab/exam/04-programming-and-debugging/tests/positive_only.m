function y = positive_only(x)
% Throws for anything not positive, so safe_apply has something to catch.
  if x <= 0
    error('positive_only:notPositive', '%g is not positive', x);
  end
  y = x;
end
