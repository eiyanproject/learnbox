function s = describe(v)
% DESCRIBE  The class and size of a value, as 'double 2x3'.
%
% class() names the type and size() gives the shape. Both work on every value,
% because in MATLAB every value is an array of something.
  s = sprintf('%s %dx%d', class(v), size(v, 1), size(v, 2));
end
