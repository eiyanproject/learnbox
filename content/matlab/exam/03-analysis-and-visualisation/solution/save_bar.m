function save_bar(filename, values, labels)
% SAVE_BAR  A labelled bar chart written as a PNG.
  if nargin < 3
    labels = {};
  end
  f = figure('visible', 'off');
  bar(values);
  if ~isempty(labels)
    set(gca, 'xtick', 1:numel(values), 'xticklabel', labels);
  end
  xlabel('category');
  ylabel('value');
  title('bar chart');
  grid on;
  print(filename, '-dpng');
  close(f);
end
