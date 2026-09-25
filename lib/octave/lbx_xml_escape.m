function out = lbx_xml_escape(s)
% LBX_XML_ESCAPE  The five characters XML will not carry literally.
% An assertion message can contain any of them - < and & most often, because
% they show up in matrix comparisons and in "expected X & got Y" text.
  if ~ischar(s)
    s = lbx_show(s);
  end
  out = s;
  out = strrep(out, "&",  "&amp;");
  out = strrep(out, "<",  "&lt;");
  out = strrep(out, ">",  "&gt;");
  out = strrep(out, "\"", "&quot;");
  out = strrep(out, "'",  "&apos;");
  % Newlines are legal in an attribute but are normalised to spaces by most
  % parsers, so collapse them here where the result is predictable.
  out = strrep(out, "\n", " | ");
end
