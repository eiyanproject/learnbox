function out = to_sizes(c)
% TO_SIZES  An ordinal categorical over small, medium and large.
%
% The value set fixes both the membership and the ORDER. Anything outside it
% becomes <undefined>, so a typo shows up as missing rather than as a new
% category with one member.
  out = categorical(c, {'small', 'medium', 'large'}, 'Ordinal', true);
end
