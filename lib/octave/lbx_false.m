function lbx_false(cond, because)
  if ~isscalar(cond) || ~(islogical(cond) || isnumeric(cond))
    lbx_fail("expected a single true/false, got %s", lbx_show(cond));
  end
  if cond
    if nargin > 1
      lbx_fail("%s", because);
    end
    lbx_fail("expected false, got true");
  end
end
