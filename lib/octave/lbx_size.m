function lbx_size(expected, actual)
% LBX_SIZE  Shape check on its own, for when the values do not matter.
  got = size(actual);
  if ~isequal(expected(:)', got)
    lbx_fail("expected size %s, got %s", mat2str(expected(:)'), mat2str(got));
  end
end
