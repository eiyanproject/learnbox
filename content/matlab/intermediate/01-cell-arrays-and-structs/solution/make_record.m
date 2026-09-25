function r = make_record(name, age)
% MAKE_RECORD  A struct with name and age.
%
% Assigning fields one at a time rather than struct('name', name, ...): when a
% value is a cell, struct() builds a struct ARRAY instead of one struct with a
% cell in it, which is a surprise worth avoiding here.
  r.name = name;
  r.age = age;
end
