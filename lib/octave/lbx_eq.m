function lbx_eq(expected, actual)
% LBX_EQ  Exact equality, via isequal so it works for matrices, char, cells
% and structs as well as scalars.
  if ~isequal(expected, actual)
    if isnumeric(expected) && isnumeric(actual) && ~isequal(size(expected), size(actual))
      lbx_fail("expected size %s, got %s", ...
               mat2str(size(expected)), mat2str(size(actual)));
    end
    lbx_fail("expected %s, got %s", lbx_show(expected), lbx_show(actual));
  end
end
