function save_plot(filename, x, y, titleText)
% SAVE_PLOT  Draw x against y, label it, and save it as a PNG.
%
% 'visible', 'off' is what lets this run with no screen. The figure is closed
% at the end: figures accumulate, each holding its data, and a loop that draws
% many without closing them will exhaust memory.
  if nargin < 4
    titleText = 'plot';
  end
  f = figure('visible', 'off');
  plot(x, y);
  xlabel('x');
  ylabel('y');
  title(titleText);
  grid on;
  print(filename, '-dpng');
  close(f);
end
