function ok = bar_is_png()
  name = 'check_bar.png';
  save_bar(name, [3 1 2], {'a', 'b', 'c'});
  fid = fopen(name, 'r');
  magic = fread(fid, 4, 'uint8')';
  fclose(fid);
  delete(name);
  ok = isequal(magic, [137 80 78 71]);
end
