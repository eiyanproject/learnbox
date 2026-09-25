function [total, used] = sum_until(v, limit)
% SUM_UNTIL  Add elements in order while the total stays within limit.
%
% Returns the total and how many elements went into it. It stops at the first
% element that would take it over, rather than skipping that one and carrying
% on - "until" means until.
  total = 0;
  used = 0;
  for i = 1:numel(v)
    if total + v(i) > limit
      break;
    end
    total = total + v(i);
    used = used + 1;
  end
end
