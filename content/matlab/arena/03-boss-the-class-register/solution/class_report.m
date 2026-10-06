function report = class_report(names, scores)
% CLASS_REPORT  Summarise a students-by-tests matrix of marks with NaN gaps.
  if numel(names) ~= size(scores, 1)
    error('class_report:size', 'expected one row of scores per name');
  end

  valid = ~isnan(scores);
  filled = scores;
  filled(~valid) = 0;

  averages = safe_divide(sum(filled, 2), sum(valid, 2));
  test_means = safe_divide(sum(filled, 1), sum(valid, 1));

  [~, top] = max(averages);  % max returns the first of several equal

  report.averages = averages;
  report.test_means = test_means;
  report.best = names{top};
  report.passed = reshape(names(averages >= 60), 1, []);
  report.missing = sum(~valid(:));
end

function out = safe_divide(totals, counts)
% Elementwise totals ./ counts, with 0 where there was nothing to count.
  out = zeros(size(totals));
  has = counts > 0;
  out(has) = totals(has) ./ counts(has);
end
