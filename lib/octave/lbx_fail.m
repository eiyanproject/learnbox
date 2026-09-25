function lbx_fail(fmt, varargin)
% LBX_FAIL  Fail the current check. Every lbx_* assertion ends up here, so the
% identifier is the one thing lbx_run needs to tell an expectation that did not
% hold apart from code that fell over.
  error("lbx:failed", fmt, varargin{:});
end
