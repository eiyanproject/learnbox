function id = error_id_of(f)
% ERROR_ID_OF  The identifier the call throws, or '' when it throws nothing.
%
% Deliberately catches everything, because reporting WHICH error happened is
% the whole job here. Ordinary code should catch only what it can handle and
% rethrow the rest.
  id = '';
  try
    f();
  catch err
    id = err.identifier;
  end
end
