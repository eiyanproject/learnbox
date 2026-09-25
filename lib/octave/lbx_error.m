function err = lbx_error(identifier, thunk)
% LBX_ERROR  The thunk must throw, with this error identifier.
%
%   lbx_error("Account:badAmount", @() deposit(a, -1))
%
% Identifier rather than message: the message is for a person to read and may
% be reworded, while the identifier is the part code is allowed to depend on.
  try
    thunk();
  catch err
    if ~strcmp(err.identifier, identifier)
      lbx_fail("expected the error %s, got %s (%s)", ...
               identifier, err.identifier, strtrim(err.message));
    end
    return;
  end
  lbx_fail("expected the error %s, but nothing was thrown", identifier);
end
