function value = rep_field(names, scores, field)
  report = class_report(names, scores);
  value = report.(field);
end
