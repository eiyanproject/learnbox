function u = used_of(v, limit)
  [~, u] = sum_until(v, limit);
end
