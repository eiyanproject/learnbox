function n = figures_left_open()
  close all;
  name = 'check_close.png';
  [x, y] = sine_data(20);
  save_plot(name, x, y, 'check');
  delete(name);
  n = numel(get(0, 'children'));
end
