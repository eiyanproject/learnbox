function lbx_true(cond, because)
% LBX_TRUE  The condition must be true. A non-scalar is rejected rather than
% quietly reduced: in MATLAB `if [1 0]` is false, which is a trap worth not
% hiding inside an assertion.
  if ~isscalar(cond) || ~(islogical(cond) || isnumeric(cond))
    lbx_fail("expected a single true/false, got %s", lbx_show(cond));
  end
  if ~cond
    if nargin > 1
      lbx_fail("%s", because);
    end
    lbx_fail("expected true, got false");
  end
end
