function out = safe_apply(f, v)
% SAFE_APPLY  f applied to each element, with NaN wherever it fails.
%
% The try sits INSIDE the loop, so one bad element does not stop the rest -
% which is the whole reason to write this rather than arrayfun. A result that
% is not a single number is treated as a failure too, because there is nowhere
% to put it.
  out = nan(size(v));
  for i = 1:numel(v)
    try
      r = f(v(i));
      if isnumeric(r) && isscalar(r)
        out(i) = r;
      end
    catch
      % leave it as NaN: this function's contract is that it never throws
    end
  end
end
