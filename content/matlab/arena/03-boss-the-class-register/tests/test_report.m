names = {'ana', 'bo', 'cy'};
scores = [ 80  90 100
           50 NaN  60
          NaN NaN NaN ];

full_names = {'dee', 'eli'};
full = [70 50; 60 60];

level_names = {'x', 'y', 'z'};
level = [50 90; 90 50; 70 70];

lbx_run({
  'averages_skip_missing',        @() lbx_near([90; 55; 0], rep_field(names, scores, 'averages'))
  'averages_are_a_column',        @() lbx_eq([3 1], size(rep_field(names, scores, 'averages')))
  'test_means_skip_missing',      @() lbx_near([65 90 80], rep_field(names, scores, 'test_means'))
  'test_means_are_a_row',         @() lbx_eq([1 3], size(rep_field(names, scores, 'test_means')))
  'best_student',                 @() lbx_str_eq('ana', rep_field(names, scores, 'best'))
  'passed_students',              @() lbx_eq({'ana'}, rep_field(names, scores, 'passed'))
  'missing_count',                @() lbx_eq(4, rep_field(names, scores, 'missing'))
  'no_gaps_averages',             @() lbx_near([60; 60], rep_field(full_names, full, 'averages'))
  'no_gaps_test_means',           @() lbx_near([65 55], rep_field(full_names, full, 'test_means'))
  'no_gaps_missing_is_zero',      @() lbx_eq(0, rep_field(full_names, full, 'missing'))
  'sixty_is_a_pass',              @() lbx_eq({'dee', 'eli'}, rep_field(full_names, full, 'passed'))
  'passed_is_a_row_cell',         @() lbx_eq([1 2], size(rep_field(full_names, full, 'passed')))
  'level_best_is_the_earliest',   @() lbx_str_eq('x', rep_field(level_names, level, 'best'))
  'passed_keeps_the_order',       @() lbx_eq({'x', 'y', 'z'}, rep_field(level_names, level, 'passed'))
  'nobody_passed',                @() lbx_eq([1 0], size(rep_field({'a', 'b'}, [10 20; 30 NaN], 'passed')))
  'one_student_averages',         @() lbx_near(75, rep_field({'solo'}, [70 NaN 80], 'averages'))
  'one_student_test_means',       @() lbx_near([70 0 80], rep_field({'solo'}, [70 NaN 80], 'test_means'))
  'one_student_best',             @() lbx_str_eq('solo', rep_field({'solo'}, [70 NaN 80], 'best'))
  'one_test',                     @() lbx_near([40; 80], rep_field({'a', 'b'}, [40; 80], 'averages'))
  'one_test_mean',                @() lbx_near(60, rep_field({'a', 'b'}, [40; 80], 'test_means'))
  'a_test_nobody_took',           @() lbx_near([50 0], rep_field({'a', 'b'}, [40 NaN; 60 NaN], 'test_means'))
  'names_as_a_column_cell',       @() lbx_eq({'ana'}, rep_field(names(:), scores, 'passed'))
  'too_few_names',                @() lbx_error('class_report:size', @() class_report({'a'}, [1 2; 3 4]))
  'too_many_names',               @() lbx_error('class_report:size', @() class_report({'a', 'b', 'c'}, [1 2; 3 4]))
});
