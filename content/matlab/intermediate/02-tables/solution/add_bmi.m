function out = add_bmi(t)
% ADD_BMI  The table with a BMI variable added: weight over height squared.
%
% ./ and .^ are element-wise; / and ^ would be a matrix division and a matrix
% power, which for two columns of the same height is not an error - just the
% wrong answer.
  out = t;
  out.BMI = t.Weight ./ t.Height .^ 2;
end
