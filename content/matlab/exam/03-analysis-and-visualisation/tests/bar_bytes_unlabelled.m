function n = bar_bytes_unlabelled()
  name = 'check_bar2.png';
  save_bar(name, [1 2 3]);
  info = stat(name);
  n = info.size;
  delete(name);
end
