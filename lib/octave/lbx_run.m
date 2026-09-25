function lbx_run(cases)
% LBX_RUN  Run a lesson's checks and write the report the grader reads.
%
% Not Octave's own %!test blocks and not matlab.unittest: the first is not
% MATLAB syntax, and the second does not exist in Octave. This is one function
% that takes an Nx2 cell array of {name, thunk} and writes JUnit XML, which the
% runner already parses for pytest, JUnit, ctest and C#.
%
%   lbx_run({
%     "adds_two_numbers",  @() lbx_eq(5, add(2, 3))
%     "handles_negatives", @() lbx_eq(-1, add(2, -3))
%   });
%
% A thunk that returns without throwing has passed. Every lbx_* assertion
% throws with the identifier "lbx:failed", so anything else that comes out is
% an error in the lesson's code rather than a failed expectation - and the
% report says which.

  if ~iscell(cases) || size(cases, 2) ~= 2
    error("lbx:usage", "lbx_run expects an Nx2 cell array of {name, thunk}");
  end

  n = size(cases, 1);
  names = cell(n, 1);
  failures = cell(n, 1);   % empty when the case passed
  failed = 0;

  for i = 1:n
    names{i} = cases{i, 1};
    thunk = cases{i, 2};
    try
      thunk();
      failures{i} = "";
    catch err
      failed = failed + 1;
      if strcmp(err.identifier, "lbx:failed")
        failures{i} = err.message;
      else
        % An error the lesson did not expect. Say so plainly rather than
        % presenting it as a failed assertion.
        failures{i} = sprintf("unexpected error: %s", err.message);
      end
    end
  end

  % Write to a temporary name and rename, so a half-written report is never
  % read as a complete one if the process is killed mid-write.
  tmp = ".lbx-report.partial";
  fid = fopen(tmp, "w");
  if fid < 0
    error("lbx:io", "cannot write the test report in %s", pwd());
  end
  fprintf(fid, "<testsuite name=\"lbx\" tests=\"%d\" failures=\"%d\">\n", n, failed);
  for i = 1:n
    fprintf(fid, "  <testcase classname=\"lbx\" name=\"%s\"", lbx_xml_escape(names{i}));
    if isempty(failures{i})
      fprintf(fid, "></testcase>\n");
    else
      fprintf(fid, "><failure message=\"%s\"></failure></testcase>\n", ...
              lbx_xml_escape(failures{i}));
    end
  end
  fprintf(fid, "</testsuite>\n");
  fclose(fid);
  rename(tmp, "TEST-lbx.xml");

  for i = 1:n
    if ~isempty(failures{i})
      printf("FAIL %s\n     %s\n", names{i}, failures{i});
    end
  end
  printf("\n%d tests, %d failed\n", n, failed);

  exit(failed > 0);
end
