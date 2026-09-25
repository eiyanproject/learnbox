function lbx_str_eq(expected, actual)
% LBX_STR_EQ  Character-array equality, with a message that shows both.
  if ~ischar(actual)
    lbx_fail("expected the text %s, got %s", lbx_show(expected), lbx_show(actual));
  end
  if ~strcmp(expected, actual)
    lbx_fail("expected \"%s\", got \"%s\"", expected, actual);
  end
end
