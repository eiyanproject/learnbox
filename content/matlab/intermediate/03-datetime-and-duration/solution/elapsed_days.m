function n = elapsed_days(d1, d2)
% ELAPSED_DAYS  The number of days from d1 to d2.
%
% d2 - d1 is a duration. days() is what turns it into a number, and writing it
% out is what stops the units being forgotten.
  n = days(d2 - d1);
end
