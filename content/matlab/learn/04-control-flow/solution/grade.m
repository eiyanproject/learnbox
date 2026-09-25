function letter = grade(score)
% GRADE  The letter grade for a score out of 100.
%
% Validate before deciding: an out-of-range score is a caller's mistake, and
% silently returning 'F' for -5 would hide it.
  if score < 0 || score > 100
    error('grade:range', 'score %g is not between 0 and 100', score);
  end
  if score >= 90
    letter = 'A';
  elseif score >= 80
    letter = 'B';
  elseif score >= 70
    letter = 'C';
  elseif score >= 60
    letter = 'D';
  else
    letter = 'F';
  end
end
