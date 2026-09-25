function c = ord_pair()
% categorical(v, valueset, 'Ordinal', true) - the MATLAB form, with no
% category names between the value set and the options.
  c = categorical({"a", "b"}, {"a", "b"}, "Ordinal", true);
end
