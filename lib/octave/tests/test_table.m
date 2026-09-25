1;

function t = setfield_tbl()
  t = table([36;17;22;45], {"ada";"bob";"cat";"dan"}, "VariableNames", {"Age","Name"});
  t.Score = [1;2;3;4];
end

function t = replace_tbl()
  t = table([36;17;22;45], {"ada";"bob";"cat";"dan"}, "VariableNames", {"Age","Name"});
  t.Age = [1;1;1;1];
end

function t = badheight()
  t = table([1;2], "VariableNames", {"A"});
  t.B = [1;2;3];
end

mk = @() table([36;17;22;45], {"ada";"bob";"cat";"dan"}, ...
               "VariableNames", {"Age", "Name"});
csv = @() readtable("people.csv");

lbx_run({
  "class_is_table",              @() lbx_type("table", mk())
  "height_counts_rows",          @() lbx_eq(4, height(mk()))
  "width_counts_variables",      @() lbx_eq(2, width(mk()))
  "size_is_rows_by_vars",        @() lbx_eq([4 2], size(mk()))
  "auto_names_when_not_given",   @() lbx_str_eq("Var1", table([1;2]).Properties.VariableNames{1})
  "variable_names_property",     @() lbx_eq({"Age","Name"}, mk().Properties.VariableNames)
  "dot_access_gives_the_column", @() lbx_eq([36;17;22;45], mk().Age)
  "dot_access_keeps_the_type",   @() lbx_str_eq("ada", mk().Name{1})
  "paren_keeps_a_table",         @() lbx_type("table", mk()(1:2, :))
  "paren_row_count",             @() lbx_eq(2, height(mk()(1:2, :)))
  "paren_with_end",              @() lbx_eq(1, height(mk()(end, :)))
  "brace_reaches_the_value",     @() lbx_eq(36, mk(){1, "Age"})
  "brace_on_text_gives_char",    @() lbx_str_eq("ada", mk(){1, "Name"})
  "brace_needs_one_variable",    @() lbx_error("table:braceWidth", @() mk(){1, :})
  "logical_row_selection",       @() lbx_eq(2, height(mk()(mk().Age > 25, :)))
  "logical_selection_is_a_table",@() lbx_type("table", mk()(mk().Age > 25, :))
  "wrong_mask_length_rejected",  @() lbx_error("table:rowMask", @() mk()(logical([1 0]), :))
  "column_subset_by_name",       @() lbx_eq(1, width(mk()(:, "Age")))
  "unknown_variable_rejected",   @() lbx_error("table:noSuchVariable", @() mk()(:, "Nope"))
  "assigning_adds_a_variable",   @() lbx_eq(3, width(setfield_tbl()))
  "assigning_replaces",          @() lbx_eq([1;1;1;1], replace_tbl().Age)
  "wrong_height_rejected",       @() lbx_error("table:heightMismatch", @() badheight())
  "mismatched_ctor_rejected",    @() lbx_error("table:heightMismatch", @() table([1;2], [1;2;3]))
  "bad_variable_name_rejected",  @() lbx_error("table:badName", @() table([1], "VariableNames", {"not a name"}))
  "duplicate_names_rejected",    @() lbx_error("table:duplicateName", @() table([1],[2], "VariableNames", {"a","a"}))
  "name_count_checked",          @() lbx_error("table:nameCount", @() table([1],[2], "VariableNames", {"a"}))
  "removevars",                  @() lbx_eq(1, width(removevars(mk(), "Name")))
  "renamevars",                  @() lbx_true(any(strcmp("Years", renamevars(mk(), "Age", "Years").Properties.VariableNames)))
  "addvars",                     @() lbx_eq(3, width(addvars(mk(), [1;2;3;4], "NewVariableNames", {"Rank"})))
  "sortrows_ascending",          @() lbx_eq([17;22;36;45], sortrows(mk(), "Age").Age)
  "sortrows_descending",         @() lbx_eq([45;36;22;17], sortrows(mk(), "Age", "descend").Age)
  "sortrows_moves_whole_rows",   @() lbx_str_eq("bob", sortrows(mk(), "Age").Name{1})
  "sortrows_on_text",            @() lbx_str_eq("ada", sortrows(mk(), "Name").Name{1})
  "bad_direction_rejected",      @() lbx_error("table:sortDirection", @() sortrows(mk(), "Age", "sideways"))
  "head_limits_rows",            @() lbx_eq(2, height(head(mk(), 2)))
  "tail_takes_the_last",         @() lbx_str_eq("dan", tail(mk(), 1).Name{1})
  "head_past_the_end_is_safe",   @() lbx_eq(4, height(head(mk(), 99)))
  "readtable_reads_the_header",  @() lbx_eq({"Name","Age","City","Score"}, csv().Properties.VariableNames)
  "readtable_row_count",         @() lbx_eq(5, height(csv()))
  "readtable_detects_numbers",   @() lbx_true(isnumeric(csv().Age))
  "readtable_keeps_text",        @() lbx_true(iscellstr(csv().City))
  "readtable_blank_becomes_nan", @() lbx_true(isnan(csv().Score(2)))
  "readtable_missing_file",      @() lbx_error("readtable:noSuchFile", @() readtable("nope.csv"))
  "a_gap_does_not_shift_columns", @() lbx_str_eq("Paris", readtable("gapped.csv").City{2})
  "a_gap_in_a_numeric_column",    @() lbx_true(isnan(readtable("gapped.csv").Age(2)))
  "a_gap_in_a_text_column",       @() lbx_str_eq("", readtable("gapped.csv").City{3})
  "gapped_row_count",             @() lbx_eq(3, height(readtable("gapped.csv")))
  "gapped_column_count",          @() lbx_eq(4, width(readtable("gapped.csv")))
  "ismissing_finds_the_gap",     @() lbx_eq(1, sum(sum(ismissing(csv()))))
  "rmmissing_drops_the_row",     @() lbx_eq(4, height(rmmissing(csv())))
  "rmmissing_keeps_the_rest",    @() lbx_str_eq("ada", rmmissing(csv()).Name{1})
  "groupsummary_counts",         @() lbx_eq([1;2;2], sortrows(groupsummary(csv(), "City"), "City").GroupCount)
  "groupsummary_mean",           @() lbx_near(29, sortrows(groupsummary(csv(), "City", "mean", "Age"), "City").mean_Age(2))
  "groupsummary_max",            @() lbx_near(45, max(groupsummary(csv(), "City", "max", "Age").max_Age))
  "groupsummary_needs_numbers",  @() lbx_error("table:groupsummary", @() groupsummary(csv(), "City", "mean", "Name"))
  "empty_table_has_no_rows",     @() lbx_eq(0, height(table()))
  "table_with_a_categorical",    @() lbx_eq(2, height(table(categorical({"a";"b"}), "VariableNames", {"G"})))
  "categorical_column_groups",   @() lbx_eq(2, height(groupsummary(table(categorical({"a";"b";"a"}), [1;2;3], "VariableNames", {"G","V"}), "G")))
  "grouping_keeps_categorical",  @() lbx_type("categorical", groupsummary(table(categorical({"a";"b"}), [1;2], "VariableNames", {"G","V"}), "G").G)
  "grouping_keeps_numeric",      @() lbx_true(isnumeric(groupsummary(table([1;2;1], [1;2;3], "VariableNames", {"G","V"}), "G").G))
  "grouping_keeps_cellstr",      @() lbx_true(iscellstr(groupsummary(table({"a";"b"}, [1;2], "VariableNames", {"G","V"}), "G").G))
});
