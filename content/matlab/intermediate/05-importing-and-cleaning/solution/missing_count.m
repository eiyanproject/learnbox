function n = missing_count(t)
% MISSING_COUNT  How many missing values the table holds.
%
% ismissing gives one logical per cell and knows what missing means for each
% type - NaN for a number, '' for text - which a hand-written isnan would not.
  n = sum(sum(ismissing(t)));
end
