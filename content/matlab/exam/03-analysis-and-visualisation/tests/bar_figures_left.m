function n = bar_figures_left()
  close all;
  name = 'check_bar3.png';
  save_bar(name, [1 2], {'a', 'b'});
  delete(name);
  n = numel(get(0, 'children'));
end
