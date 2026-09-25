function ok = wrote_a_png()
% A PNG begins with the bytes 137 80 78 71 - checking the content rather than
% the extension, since naming a file .png proves nothing.
  name = 'check_magic.png';
  [x, y] = sine_data(20);
  save_plot(name, x, y, 'check');
  fid = fopen(name, 'r');
  magic = fread(fid, 4, 'uint8')';
  fclose(fid);
  delete(name);
  ok = isequal(magic, [137 80 78 71]);
end
