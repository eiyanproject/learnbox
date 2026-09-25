function n = plot_bytes()
  name = 'check_plot.png';
  [x, y] = sine_data(50);
  save_plot(name, x, y, 'check');
  info = stat(name);
  n = info.size;
  delete(name);
end
