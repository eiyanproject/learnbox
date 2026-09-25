function lbx_near(expected, actual, tol)
% LBX_NEAR  Equality within a tolerance, elementwise. Default 1e-9.
%
% Floating point is why this exists: 0.1 + 0.2 == 0.3 is false in MATLAB, in
% Octave, and in every other language using IEEE 754 doubles.
  if nargin < 3, tol = 1e-9; end
  if ~isnumeric(actual) || ~isnumeric(expected)
    lbx_fail("expected numbers, got %s and %s", lbx_show(expected), lbx_show(actual));
  end
  if ~isequal(size(expected), size(actual))
    lbx_fail("expected size %s, got %s", mat2str(size(expected)), mat2str(size(actual)));
  end
  d = abs(expected(:) - actual(:));
  if any(d > tol)
    [worst, at] = max(d);
    if isscalar(expected)
      lbx_fail("expected %.10g, got %.10g (tolerance %g)", expected, actual, tol);
    else
      lbx_fail("expected %s, got %s - worst difference %.3g at element %d", ...
               lbx_show(expected), lbx_show(actual), worst, at);
    end
  end
end
