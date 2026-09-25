function lbx_type(expected, value)
% LBX_TYPE  Class check. MATLAB is loosely typed at the surface and strict
% underneath - 1 is a double, int8(1) is not, and they do not behave the same
% on overflow or division.
  if ~strcmp(class(value), expected)
    lbx_fail("expected a %s, got a %s", expected, class(value));
  end
end
